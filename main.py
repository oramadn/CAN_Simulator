import sys
import random
from variable_frame import VariableFrame
from can_message import CANmsg
from simulation_control import SimulationControl
import primaryWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QInputDialog
from PySide6.QtCore import Slot, QTimer


class PrimaryWindow(QMainWindow, primaryWindow.Ui_primaryWindow):
    frames = 0
    variable_frames = []
    variable_frames_copy = 0
    chosen_variable_frames = []
    static_frames = []

    throttle_frame_idx = None
    throttle_byte = '00'
    throttle_byte_idx = None

    brake_frame_idx = None
    brake_byte = '00'
    brake_byte_idx = None

    steering_frame_idx = None
    steering_byte = ['00', '00']
    steering_byte_idx = None

    variable_frames_idx = []
    generated_hex_numbers = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resize(950, 1000)
        self.startButton.clicked.connect(self.start_simulation)
        self.variable_frames_timer = QTimer(self)
        self.variable_frames_timer.timeout.connect(self.simulate_variable_frames)

        # Simulation window
        self.throttleBrakeWindow = SimulationControl()

    def set_steering_byte(self):
        value = self.throttleBrakeWindow.steering_slider.value()
        if value > 127:
            scaled_value = (value - 128) * 254 // (255 - 128) + 1
            self.steering_byte[0] = '00'
            self.steering_byte[1] = format(scaled_value, '02x')
        elif value < 127:
            scaled_value = abs((value - 128) * 254 // (255 - 128) + 1)
            self.steering_byte[0] = format(scaled_value, '02x')
            self.steering_byte[1] = '00'
        else:
            self.steering_byte[0] = '00'
            self.steering_byte[1] = '00'

    def set_brake_byte(self):
        value = self.throttleBrakeWindow.brake_slider.value()
        self.brake_byte = format(value, '02x')

    def set_throttle_byte(self):
        value = self.throttleBrakeWindow.throttle_slider.value()
        self.throttle_byte = format(value, '02x')

    def update_variable_bytes(self):
        self.set_throttle_byte()
        frame = self.variable_frames_copy[self.throttle_frame_idx]
        data = frame.data
        frame.data = data[:self.throttle_byte_idx] + self.throttle_byte + data[self.throttle_byte_idx + 2:]

        self.set_brake_byte()
        frame = self.variable_frames_copy[self.brake_frame_idx]
        data = frame.data
        frame.data = data[:self.brake_byte_idx] + self.brake_byte + data[self.brake_byte_idx + 2:]

        self.set_steering_byte()
        frame = self.variable_frames_copy[self.steering_frame_idx]
        data = frame.data
        replacements = {self.steering_byte_idx[0]: self.steering_byte[0],
                        self.steering_byte_idx[1]: self.steering_byte[1]}

        # Start by breaking down the string into parts that will not change
        parts = [
            data[:min(replacements.keys())]  # Start to first replacement
        ]

        # Sort indices to handle replacements in order
        sorted_indices = sorted(replacements.keys())

        for i in range(len(sorted_indices)):
            idx = sorted_indices[i]
            # Add new value
            parts.append(replacements[idx])
            # Determine the next segment start
            if i + 1 < len(sorted_indices):
                next_idx = sorted_indices[i + 1]
                parts.append(data[idx + 2:next_idx])
            else:
                # Handle the last part of the string after the last replacement
                parts.append(data[idx + 2:])

        # Join all parts together to form the new string
        frame.data = ''.join(parts)

    def simulate_variable_frames(self):
        for frame in self.chosen_variable_frames:
            self.update_variable_bytes()
            self.variable_frames_copy[frame.idx].data = random.choice(frame.random_hex_numbers)
            self.clear_table()
            self.generate_table(self.variable_frames_copy + self.static_frames)

    def generate_fixed_hex(self, num_of_random_hex):
        # Calculate the number of bytes the hex number should have
        num_bytes = 8  # Each byte is represented by two hex characters
        # random.seed(42)
        for frame in self.chosen_variable_frames:
            for _ in range(random.randint(2, num_of_random_hex)):
                # Generate a random integer with the right number of bits (8 bits per byte)
                random_int = random.getrandbits(num_bytes * 8)
                # Convert integer to a hexadecimal string, and format to ensure correct length
                random_hex = format(random_int, '0{}x'.format(num_bytes * 2))
                # Append the formatted hex string to the list
                frame.random_hex_numbers.append(random_hex)

    def generate_variable_byte_idx(self, flag=0):
        if flag == 1:
            even_indices = list(range(0, 16, 2))
            selected_indices = random.sample(even_indices, 2)  # Randomly pick two unique indices
            return selected_indices
        even_indices = range(0, 16, 2)
        selected_index = random.choice(even_indices)
        return selected_index

    def generate_variable_frames(self):
        frames = list(range(len(self.variable_frames)))
        random.shuffle(frames)
        self.throttle_frame_idx, self.brake_frame_idx, self.steering_frame_idx, self.variable_frames_idx = frames[0], \
            frames[1], frames[2], frames[3:]

    def clear_table(self):
        self.mainTable.clearContents()
        self.mainTable.setRowCount(0)

    def add_row(self, row_data):
        row_position = self.mainTable.rowCount()
        self.mainTable.insertRow(row_position)
        for column, data in enumerate(row_data):
            item = QTableWidgetItem(str(data))
            self.mainTable.setItem(row_position, column, item)

    def generate_table(self, frames):
        data_row = []
        # Format the data such that it can fit into 9 columns (ID , 0-7) where each column has 1 byte
        for frame in frames:
            data_row.append("0x" + frame.id)
            for i in range(0, len(frame.data), 2):
                data_row.append("0x" + frame.data[i:i + 2])
            data_row_copy = data_row.copy()
            self.add_row(data_row_copy)
            data_row.clear()

    def split_frames(self, ratio=0.6):
        random.shuffle(self.frames)

        split_index = int(len(self.frames) * ratio)

        self.variable_frames = self.frames[:split_index]
        self.static_frames = self.frames[split_index:]

    def generate_frames(self, frame_count):
        # Generate random IDs and DATA
        data = []
        for i in range(frame_count):
            random_id = hex(random.randint(0, 2 ** 11 - 1))[2:].rjust(5, '0')
            random_data = hex(random.randint(0, 2 ** 64 - 1))[2:].rjust(16, '0')

            data.append(CANmsg(random_id, random_data))

        self.frames = sorted(data, key=lambda x: x.id)

    def open_input_dialog(self):
        while True:
            frame_count, ok = QInputDialog.getText(self, 'Input Dialog',
                                                   'How many frames would you like to generate (10-100)?: ')
            if ok:
                try:
                    if 10 <= int(frame_count) <= 100:
                        return int(frame_count)
                except ValueError:
                    print("\nInvalid input")
                    continue
            else:
                return 0

    @Slot()
    def start_simulation(self):
        print("Simulation start")
        frame_count = self.open_input_dialog()

        # Generate the frames
        self.generate_frames(frame_count)

        if frame_count != 0:  # If the user hits cancel when prompted to enter number of needed frames
            # Split data in variable and static frames with a ratio of 0.6 to 0.4
            self.split_frames()
            self.variable_frames_copy = self.variable_frames.copy()

            self.generate_table(self.frames)
            self.startButton.hide()  # Grey out the start button

            # Generate indices for throttle, break, steering and the rest
            self.generate_variable_frames()

            # Create VariableFrame objects using the variable frame indices
            for i in self.variable_frames_idx:
                self.chosen_variable_frames.append(VariableFrame(self.variable_frames[i].id,
                                                                 self.variable_frames[i].data, i))

            # Generate random frames for the variable frames
            self.generate_fixed_hex(5)

            self.throttle_byte_idx = self.generate_variable_byte_idx()
            self.brake_byte_idx = self.generate_variable_byte_idx()
            self.steering_byte_idx = self.generate_variable_byte_idx(1)
            print(self.variable_frames_copy[self.steering_frame_idx].id)
            print(self.steering_byte_idx)

            # Start the simulation
            self.variable_frames_timer.start(50)  # Call every 1000 milliseconds (1 second)
            self.throttleBrakeWindow.show()
            print("Program ended")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = PrimaryWindow()
    window.show()

    sys.exit(app.exec())
