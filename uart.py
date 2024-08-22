import serial
import time

# Configuration for serial communication
ser = serial.Serial(
    port='COM4',       # Replace with your COM port
    baudrate=115200,   # Baud rate
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bit
    bytesize=serial.EIGHTBITS,  # 8 data bits
    timeout=1  # Read timeout in seconds
)

# Ensure the port is open
if not ser.is_open:
    ser.open()

# Data to be transmitted
TX = [0x55, 0xAA, 0x07, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x87, 0xF0]  # Example data array, replace with your own data

# Sending data
ser.write(bytearray(TX))

# Allow some time for response (if expected)
time.sleep(1)

# Reading the received data
while ser.in_waiting > 0:
    received_data = ser.read(ser.in_waiting)  # Read all available data
    print(f"Received: {received_data}")

# Close the serial port
ser.close()
