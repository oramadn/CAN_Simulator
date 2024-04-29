import sys
import random
from variable_frame import VariableFrame
from can_message import CANmsg
from slider_widget import SliderWidget, MyDevice
import primaryWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QInputDialog
from PySide6.QtCore import Slot, QTimer


class PrimaryWindow(QMainWindow, primaryWindow.Ui_primaryWindow):
    frames = 0
    variable_frames = []
    variable_frames_copy = 0
    chosen_variable_frames = []
    static_frames = []
    throttle_idx = 0
    brake_idx = 0
    steering_idx = []
    variable_frames_idx = []
    generated_hex_numbers = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resize(950, 1000)
        self.startButton.clicked.connect(self.start_simulation)
        self.variable_frames_timer = QTimer(self)
        self.variable_frames_timer.timeout.connect(self.simulate_variable_frames)

    def simulate_variable_frames(self):
        for frame in self.chosen_variable_frames:
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

    def generate_variable_frames(self):
        frames = list(range(len(self.variable_frames)))
        random.shuffle(frames)
        self.throttle_idx, self.brake_idx, self.steering_idx, self.variable_frames_idx = frames[0], frames[1], frames[
                                                                                                               2:4], frames[
                                                                                                                     4:]

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

            # Start the simulation
            self.variable_frames_timer.start(1000)  # Call every 1000 milliseconds (1 second)
            slider_window.show()

            print("Program ended")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = PrimaryWindow()
    window.show()

    device = MyDevice()
    slider_window = SliderWidget(device)

    sys.exit(app.exec())
