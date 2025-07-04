import logging
import serial
import struct
import numpy as np

from helperFunctions import *

HEADER		    = 0x55
TAIL		    = 0xAA
ID_ACK		    = 0x00
ID_NACK		    = 0x01
ID_START	    = 0x02
ID_DATA		    = 0x03
ID_RET		    = 0x04
ID_ABORT	    = 0x05
FRAME_DATA_LEN  = 128

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

def send_cmd_frame(ser: serial.Serial, id):
    """
    Sends an command frame to the hardware
    Frame structure:
        - Header (0x55)
        - Frame ID
        - CRC16 (2 bytes)
        - Tail (0xAA)
    """
    header = bytes([HEADER, id])  # Header and frame ID
    crc = calculate_crc16(header)  # CRC16 of header + payload
    crc_bytes = struct.pack('<H', crc)
    tail = bytes([TAIL])  # Tail byte

    frame = header + crc_bytes + tail

    ser.write(frame)
    if   id == ID_ACK:   logging.info("Sent ACK frame to hardware.")
    elif id == ID_NACK:  logging.info("Sent NACK frame to hardware.")
    elif id == ID_START: logging.info("Sent START frame to hardware.")
    elif id == ID_ABORT: logging.info("Sent ABORT frame to hardware.")
    else:                logging.warning("Sent unspecified frame to hardware!")

def receive_ack_nack(ser: serial.Serial) -> bool:
    # Wait for response
    response = ser.read(5)
    if len(response) == 5 and response[0] == HEADER and response[4] == TAIL:
        response_crc = struct.unpack('<H', response[2:4])[0]
        expected_crc = calculate_crc16(response[0:2])  # CRC on bytes header and ID bytes
        if response_crc == expected_crc:
            if response[1] == ID_ACK:  # ACK received
                logging.info(f"Received ACK frame, hardware ready.")
                return True
            else:
                logging.warning("Received NACK frame.")
                return False
        else:
            logging.error("Received frame with incorrect CRC.")
            return False
    else:
        logging.error("Malformed response frame received.")
        return False

def send_initialization_frame(ser: serial.Serial, retries: int = 3) -> bool:
    """
    Sends an initialization frame to the hardware and waits for ACK/NACK.
    Retries the process if necessary.
    """
    for attempt in range(retries):
        send_cmd_frame(ser, ID_START)
        logging.info(f"Waiting for ACK/NACK... (Attempt {attempt+1}/{retries})")

        if receive_ack_nack(ser) == True: # Wait for response
            return True # If ACK received, end function, else retry

    logging.error("Failed to receive valid ACK/NACK after retries.")
    return False

def send_image_data(ser: serial.Serial, img: np.ndarray, retries: int = 3) -> bool:
    """
    Sends image data to the hardware in 128-byte chunks.
    If the image is smaller than 128 bytes, it pads with 0s.
    """
    if img.dtype != np.uint16:
        logging.error("Image data must be of type uint16.")
        return False

    image_data = img.tobytes()  # Convert image to byte array
    # Each chunk = 128 uint16 pixels → 256 bytes
    chunk_size_pixels = 128
    chunk_size_bytes = chunk_size_pixels * 2  # 256 bytes

    # Convert to uint16 array for clean slicing
    image_data_uint16 = np.frombuffer(image_data, dtype=np.uint16)
    total_pixels = len(image_data_uint16)

    # Split into chunks of 128 pixels
    chunks = [image_data_uint16[i:i + chunk_size_pixels].tobytes()
              for i in range(0, total_pixels, chunk_size_pixels)]

    # Pad last chunk if needed
    if len(chunks[-1]) < chunk_size_bytes:
        chunks[-1] = chunks[-1] + b'\x00' * (chunk_size_bytes - len(chunks[-1]))


    for chunk_number, chunk in enumerate(chunks):
        header = bytes([HEADER, ID_DATA])  # Frame header and ID
        chunk_number_bytes = struct.pack('<H', chunk_number)  # 16-bit chunk number, little-endian

        payload = chunk  # Payload is the image data chunk

        crc_input = header + chunk_number_bytes + payload
        crc = calculate_crc16(crc_input)
        crc_bytes = struct.pack('<H', crc)

        tail = bytes([TAIL])

        frame = crc_input + crc_bytes + tail
        logging.info(f"Sending image data frame: {frame.hex()}")

        for attempt in range(retries):
            ser.write(frame)  # Send the frame
            logging.info(f"Image data frame sent, waiting for ACK/NACK... (Attempt {attempt+1}/{retries})")

            if receive_ack_nack(ser) == True: # Wait for response
                break #return True # If ACK received, transmit next chunk, else retry
            elif attempt == retries - 1: # This was last retry and it was unsuccesful
                logging.error("Failed to receive valid ACK/NACK after retries.")
                return False # Return failure
            
    return True

def receive_hardware_results(ser: serial.Serial) -> tuple:
    """
    Receives the result frame from the hardware and parses the data.
    After receiving, sends ACK frame to hardware and returns the parsed results.
    """
    # expected_length = 130
    # expected_length = 82
    expected_length = 86
    raw = ser.read(expected_length)
    lenght = len(raw)
    if lenght != expected_length:
        logging.error(f"Incomplete hardware result frame. Expected {expected_length}, got {len(raw)}")
        return default_response()

    if raw[0] != HEADER or raw[-1] != TAIL:
        logging.error("Malformed hardware result frame.")
        return default_response()

    # Validate CRC
    # payload_with_header = raw[:127]  # up to and including payload
    payload_with_header = raw[:83]  # up to and including payload
    expected_crc = calculate_crc16(payload_with_header)
    received_crc = struct.unpack('<H', raw[83:85])[0]

    if expected_crc != received_crc:
        logging.error(f"CRC mismatch in result frame. Expected {expected_crc:04X}, got {received_crc:04X}")
        return default_response()

    # Parse payload
    payload = raw[2:83]  # Skip header and frame ID

    # Unpack: 9d, 3d, B, 8H, I, f, f
    #fmt = '<9d3dB8HIff'
    fmt = '<3d3dB8H3If'
    unpacked = struct.unpack(fmt, payload)

    R_vals = unpacked[0:3]
    t_vals = unpacked[3:6]
    success_flag = unpacked[6]
    points_vals = unpacked[7:15]
    hw_time_val = unpacked[15]
    total_time_val = unpacked[16]
    found_peak_num_val = unpacked[17]
    temp_val = unpacked[18]

    #R_vals = unpacked[0:9]
    #t_vals = unpacked[9:12]
    #success_flag = unpacked[12]
    #points_vals = unpacked[13:21]
    #time_val = unpacked[21]
    #current_val = unpacked[22]
    #temp_val = unpacked[23]

    R = np.array(R_vals, dtype=np.float64).reshape((3,))
    t = np.array(t_vals, dtype=np.float64).reshape((3,))
    success = bool(success_flag)
    points = np.array(points_vals, dtype=np.uint16).reshape((4, 2))
    hw_time = np.uint32(hw_time_val)
    total_time = np.uint32(total_time_val)
    found_peak_num = float(found_peak_num_val)
    temp = float(temp_val)

    logging.info("Hardware result frame successfully received and parsed.")

    # Send ACK frame
    send_cmd_frame(ser, ID_ACK)

    return R, t, success, points, hw_time, total_time, found_peak_num, temp

def default_response():
    """
    Returns default response in case of errors or failure.
    """
    return np.zeros((3,)), np.zeros((1, 3)), False, np.zeros((4, 2), dtype=np.uint16), 0, 0, 0, 0.0

def send_to_hardware(img, com_port, baud_rate, max_retries=3):
    """
    Sends image to hardware and receives results.
    The process involves initialization, image transmission, and receiving results.
    """
    try:
        with serial.Serial(port=com_port, baudrate=baud_rate, timeout=10) as ser:
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
