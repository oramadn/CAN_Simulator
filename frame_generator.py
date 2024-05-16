import random
import serial
import threading
import json
import time

random.seed(42)
SPLIT_RATIO = 0.6
NUM_OF_RANDOM_HEX_FRAMES = 5
lock = threading.Lock()

frame_count = int(input("Enter required number of CAN frames (10-100): "))

frames = []
# Generate static frames
for _ in range(int(frame_count * (1 - SPLIT_RATIO))):
    random_id = hex(random.randint(0, 2 ** 11 - 1))[2:].rjust(5, '0')
    random_data = hex(random.randint(0, 2 ** 64 - 1))[2:].rjust(16, '0')

    frames.append({'id': random_id, 'data': random_data})

# Generate variable frames
for _ in range(int(frame_count * SPLIT_RATIO)):
    random_id = hex(random.randint(0, 2 ** 11 - 1))[2:].rjust(5, '0')
    hex_values = []
    for _ in range(random.randint(2, NUM_OF_RANDOM_HEX_FRAMES)):
        # Generate a random integer with the right number of bits (8 bits per byte)
        random_int = random.getrandbits(64)
        # Convert integer to a hexadecimal string, and format to ensure correct length
        random_hex = format(random_int, '0{}x'.format(16))
        # Append the formatted hex string to the list
        hex_values.append(random_hex)
    frames.append({'id': random_id, 'data': hex_values})
random.shuffle(frames)

json_data = json.dumps(frames)
print(json_data)


# Set up the serial port connection
ser = serial.Serial('COM4', 9600, timeout=1)  # Replace 'COM3' with your Arduino port
ser.flush()
while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
