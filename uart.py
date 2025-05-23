import logging
import serial
import struct
import numpy as np

def calculate_crc16(data: bytes) -> int:
    """
    Calculates CRC16 for the provided data using the standard CRC-16-ANSI method.
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def send_initialization_frame(ser: serial.Serial, retries: int = 3) -> bool:
    """
    Sends an initialization frame to the hardware and waits for ACK/NACK.
    Retries the process if necessary.
    """
    header = bytes([0x55, 0x03])  # Frame header and ID
    crc = calculate_crc16(header)  # Calculate CRC16
    crc_bytes = struct.pack('<H', crc)
    tail = bytes([0xAA])

    frame = header + crc_bytes + tail
    logging.info(f"Sending initialization frame: {frame.hex()}")

    for attempt in range(retries):
        ser.write(frame)  # Send the initialization frame
        logging.info(f"Initialization frame sent, waiting for ACK/NACK... (Attempt {attempt+1}/{retries})")

        # Wait for response
        response = ser.read(5)
        if len(response) == 5 and response[0] == 0x55 and response[1] == 0x03 and response[4] == 0xAA:
            response_crc = struct.unpack('<H', response[2:4])[0]
            expected_crc = calculate_crc16(response[:2] + response[3:4])  # CRC on bytes 0,1 and 3
            if response_crc == expected_crc:
                ack_nack = response[2]
                if ack_nack == 0x01:  # ACK received
                    logging.info(f"Received ACK frame, hardware ready.")
                    return True
                else:
                    logging.warning("Received NACK frame. Retrying...")
            else:
                logging.error("Received frame with incorrect CRC. Retrying...")
        else:
            logging.error("Malformed response frame received. Retrying...")

    logging.error("Failed to receive valid ACK/NACK after retries.")
    return False


def send_image_data(ser: serial.Serial, img: np.ndarray, retries: int = 3) -> bool:
    """
    Sends image data to the hardware in 128-byte chunks.
    If the image is smaller than 128 bytes, it pads with 0s.
    """
    image_data = img.tobytes()  # Convert image to byte array
    image_length = len(image_data)
    chunks = [image_data[i:i + 128] for i in range(0, image_length, 128)]

    # If the last chunk is smaller than 128 bytes, pad it with 0s
    if len(chunks[-1]) < 128:
        chunks[-1] = chunks[-1] + b'\x00' * (128 - len(chunks[-1]))

    for chunk in chunks:
        header = bytes([0x55, 0x05])  # Frame header and ID
        payload = chunk  # Payload is the image data chunk
        crc = calculate_crc16(header + payload)  # CRC16 of header + payload
        crc_bytes = struct.pack('<H', crc)
        tail = bytes([0xAA])

        frame = header + payload + crc_bytes + tail
        logging.info(f"Sending image data frame: {frame.hex()}")

        for attempt in range(retries):
            ser.write(frame)  # Send the frame
            logging.info(f"Image data frame sent, waiting for ACK/NACK... (Attempt {attempt+1}/{retries})")

            # Wait for response
            response = ser.read(5)
            if len(response) == 5 and response[0] == 0x55 and response[1] == 0x03 and response[4] == 0xAA:
                response_crc = struct.unpack('<H', response[2:4])[0]
                expected_crc = calculate_crc16(response[:2] + response[3:4])  # CRC on bytes 0,1 and 3
                if response_crc == expected_crc:
                    ack_nack = response[2]
                    if ack_nack == 0x01:  # ACK received
                        logging.info(f"Received ACK frame, continuing to next chunk.")
                        break
                    else:
                        logging.warning("Received NACK frame. Retrying image chunk...")
                else:
                    logging.error("Received frame with incorrect CRC. Retrying...")
            else:
                logging.error("Malformed response frame received. Retrying...")
        else:
            logging.error("Failed to receive valid ACK/NACK after retries.")
            return False

    return True


def receive_hardware_results(ser: serial.Serial) -> tuple:
    """
    Receives the result frame from the hardware and parses the data.
    After receiving, sends ACK frame to hardware and returns the parsed results.
    """
    expected_length = 130
    raw = ser.read(expected_length)

    if len(raw) != expected_length:
        logging.error(f"Incomplete hardware result frame. Expected {expected_length}, got {len(raw)}")
        return default_response()

    if raw[0] != 0x55 or raw[1] != 0x06 or raw[-1] != 0xAA:
        logging.error("Malformed hardware result frame.")
        return default_response()

    # Validate CRC
    payload_with_header = raw[:127]  # up to and including payload
    expected_crc = calculate_crc16(payload_with_header)
    received_crc = struct.unpack('<H', raw[127:129])[0]

    if expected_crc != received_crc:
        logging.error(f"CRC mismatch in result frame. Expected {expected_crc:04X}, got {received_crc:04X}")
        return default_response()

    # Parse payload
    payload = raw[2:127]  # Skip header and frame ID

    # Unpack: 9d, 3d, B, 8H, I, f, f
    fmt = '<9d3dB8HIff'
    unpacked = struct.unpack(fmt, payload)

    R_vals = unpacked[0:9]
    t_vals = unpacked[9:12]
    success_flag = unpacked[12]
    points_vals = unpacked[13:21]
    time_val = unpacked[21]
    current_val = unpacked[22]
    temp_val = unpacked[23]

    R = np.array(R_vals, dtype=np.float64).reshape((3, 3))
    t = np.array(t_vals, dtype=np.float64).reshape((1, 3))
    success = bool(success_flag)
    points = np.array(points_vals, dtype=np.uint16).reshape((2, 4))
    time = np.uint32(time_val)
    current = float(current_val)
    temp = float(temp_val)

    logging.info("Hardware result frame successfully received and parsed.")

    # Send ACK frame
    send_ack_frame(ser)

    return R, t, success, points, time, current, temp


def send_ack_frame(ser: serial.Serial):
    """
    Sends an ACK frame to the hardware after receiving the result frame.
    Frame structure:
        - Header (0x55)
        - Frame ID (0x04 for ACK)
        - Payload (0x01 for ACK)
        - CRC16 (2 bytes)
        - Tail (0xAA)
    """
    header = bytes([0x55, 0x04])  # Header and frame ID
    payload = bytes([0x01])  # Payload for ACK
    crc = calculate_crc16(header + payload)  # CRC16 of header + payload
    crc_bytes = struct.pack('<H', crc)
    tail = bytes([0xAA])  # Tail byte

    frame = header + payload + crc_bytes + tail

    ser.write(frame)
    logging.info("Sent ACK frame to hardware.")


def default_response():
    """
    Returns default response in case of errors or failure.
    """
    return np.zeros((3, 3)), np.zeros((1, 3)), False, np.zeros((2, 4), dtype=np.uint16), 0, 0.0, 0.0


def send_to_hardware(img, com_port, baud_rate, max_retries=3):
    """
    Sends image to hardware and receives results.
    The process involves initialization, image transmission, and receiving results.
    """
    try:
        with serial.Serial(port=com_port, baudrate=baud_rate, timeout=1) as ser:
            # Step 1: Initialize communication
            if not send_initialization_frame(ser, retries=max_retries):
                logging.error("Failed to initialize hardware after retries.")
                return default_response()
    
            # Step 2: Send image data
            if not send_image_data(ser, img, retries=max_retries):
                logging.error("Failed to send image data to hardware.")
                return default_response()
    
            # Step 3: Receive result frame and send ACK
            return receive_hardware_results(ser)
    
    except serial.SerialException as e:
        logging.error(f"Serial communication error: {e}")
        return default_response()
    
    return default_response()
