import serial
import json


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def serial_read(ser):
    try:
        # Read the serial data
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        if line:
            # Check if the line is valid JSON
            if is_json(line):
                # Parse JSON data
                data = json.loads(line)
                return data
            else:
                return None
    except json.JSONDecodeError:
        print("Error decoding JSON")
    except UnicodeDecodeError as e:
        print(f"Unicode decode error: {e}")
    except KeyboardInterrupt:
        print("Exiting...")


# Example usage
if __name__ == "__main__":
    ser = serial.Serial('COM4', 500000, timeout=1)  # Adjust 'COM3' and baud rate as needed
    while True:
        received_data = serial_read(ser)
        if received_data is not None:
            print(f"Received data: {received_data}")
