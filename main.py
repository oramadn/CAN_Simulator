import sys
import random
import time
import csv
import pandas as pd
import threading

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QInputDialog, QVBoxLayout
from PySide6.QtCore import Slot, QTimer
from PySide6.QtGui import QBrush, QColor

from variable_frame import VariableFrame
from can_message import CANmsg
from simulation_control import SimulationControl
import primaryWindow
import model_train
from realtime_predictor import RealTimePredictor
from linear_map_frame import analyze_linear_relationship_per_frame
from plotter import RealTimePlotter


class PrimaryWindow(QMainWindow, primaryWindow.Ui_primaryWindow):
    DEFAULT_THROTTLE_BRAKE_BYTE = '00'
    DEFAULT_STEERING_BYTES = ['00', '00']
    DEFAULT_DURATION = 500
    RANDOM_SEED = 42

    # Indices and settings for variable frame simulation
    variable_frames = []
    variable_frames_copy = None
    variable_frames_idx = []
    chosen_variable_frames = []

    # Indices and settings for throttle controls
    throttle_frame_idx = None
    throttle_byte = DEFAULT_THROTTLE_BRAKE_BYTE
    throttle_byte_idx = None

    # Indices and settings for brake controls
    brake_frame_idx = None
    brake_byte = DEFAULT_THROTTLE_BRAKE_BYTE
    brake_byte_idx = None

    # Indices and settings for steering controls
    steering_frame_idx = None
    steering_byte = DEFAULT_STEERING_BYTES
    steering_byte_idx = None

    # Additional settings for simulation
    frames = None
    frame_count = None
    file_paths = {
        'data/Idle_data.csv': 'Idle',
        'data/Throttle_data.csv': 'Throttle',
        'data/Brake_data.csv': 'Brake',
        'data/SteerRight_data.csv': 'SteerRight',
        'data/SteerLeft_data.csv': 'SteerLeft'
    }
    static_frames = []
    generated_hex_numbers = []

    # Capture settings
    captured_can_frames = []
    capture_cnt = 0
    capture_mode = None

    predictor = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resize(950, 1000)

        # Timer setup for simulation of variable frames
        self.variable_frames_timer = QTimer(self)
        self.variable_frames_timer.timeout.connect(self.simulate_variable_frames)

        # Event connections
        self.startButton.clicked.connect(self.start_simulation)
        self.captureIdleButton.clicked.connect(self.enable_capture)
        self.captureThrottleButton.clicked.connect(self.enable_capture)
        self.captureBrakeButton.clicked.connect(self.enable_capture)
        self.captureSteerLeftButton.clicked.connect(self.enable_capture)
        self.captureSteerRightButton.clicked.connect(self.enable_capture)
        self.trainButton.clicked.connect(self.train_pipeline)
        self.loadButton.clicked.connect(self.start_predict_pipeline)
        self.findFramesButton.clicked.connect(self.find_action_frames)
        self.plotButton.clicked.connect(self.start_plotting)
        self.trainButton.hide()
        self.loadButton.hide()
        # self.findFramesButton.hide()
        self.throttleLabel.hide()
        self.brakeLabel.hide()
        self.steeringLabel.hide()

        self.simulationControlWindow = SimulationControl()
        self.simulationControlWindow.state_label.hide()


        self.capture_states = {
            'Idle': self.captureIdleButton.setEnabled,
            'Throttle': self.captureThrottleButton.setEnabled,
            'Brake': self.captureBrakeButton.setEnabled,
            'SteerLeft': self.captureSteerLeftButton.setEnabled,
            'SteerRight': self.captureSteerRightButton.setEnabled
        }

        self.capture_map = {
            'Throttle': [1, self.simulationControlWindow.throttle_slider.setValue],
            'Brake': [1, self.simulationControlWindow.brake_slider.setValue],
            'SteerLeft': [126, self.simulationControlWindow.steering_slider.setValue],
            'SteerRight': [128, self.simulationControlWindow.steering_slider.setValue],
        }

        self.found_action_frames = {}
        self.table_reference = {}

    def fetch_throttle_data(self):
        reference_data = self.variable_frames_copy[self.table_reference["Throttle"][0]].data
        reference_byte_idx = self.table_reference["Throttle"][1]

        start_pos = reference_byte_idx * 2
        byte = reference_data[start_pos:start_pos + 2]
        val = int(byte, 16)
        return val

    def fetch_brake_data(self):
        reference_data = self.variable_frames_copy[self.table_reference["Brake"][0]].data
        reference_byte_idx = self.table_reference["Brake"][1]

        start_pos = reference_byte_idx * 2
        byte = reference_data[start_pos:start_pos + 2]
        val = int(byte, 16)
        return val

    def fetch_steer_right_data(self):
        reference_data = self.variable_frames_copy[self.table_reference["SteerRight"][0]].data
        reference_byte_idx = self.table_reference["SteerRight"][1]

        start_pos = reference_byte_idx * 2
        byte = reference_data[start_pos:start_pos + 2]
        val = int(byte, 16)
        return val

    def fetch_steer_left_data(self):
        reference_data = self.variable_frames_copy[self.table_reference["SteerLeft"][0]].data
        reference_byte_idx = self.table_reference["SteerLeft"][1]

        start_pos = reference_byte_idx * 2
        byte = reference_data[start_pos:start_pos + 2]
        val = int(byte, 16)
        return val

    def start_plotting(self):
        data_fetch_functions = {
            'throttle': self.fetch_throttle_data,
            'brake': self.fetch_brake_data,
            'steer_right': self.fetch_steer_right_data,
            'steer_left': self.fetch_steer_left_data
        }
        self.plotter = RealTimePlotter()
        self.plotter.start_data_threads(data_fetch_functions)
        self.plotter.show()

    def get_color_for_action(self, action):
        if action == 'Throttle':
            return QColor(125, 40, 40)  # Red
        elif action == 'Brake':
            return QColor(55, 78, 161)  # Blue
        elif action in ['SteerRight', 'SteerLeft']:
            return QColor(90, 166, 95)  # Green
        return QColor(255, 255, 255)  # Default White

    def color_cells(self, frame_id, byte_position, color):
        for row in range(self.mainTable.rowCount()):
            frame_item = self.mainTable.item(row, 0)
            byte_item = self.mainTable.item(row, 1 + byte_position)  # Assuming byte positions start at column 1

            if frame_item and frame_item.text()[2:] == frame_id:
                byte_item.setBackground(QBrush(color))

    def find_action_frames(self):
        for file_path, action in self.file_paths.items():
            if file_path == "data/Idle_data.csv":
                continue
            best_frame_id, best_byte, best_r_squared = analyze_linear_relationship_per_frame(file_path,
                                                                                             self.frame_count)
            self.found_action_frames[action] = (best_frame_id, best_byte, best_r_squared)
            print(f"The {file_path[len("data/"):-len("_data.csv")]} frame ID is {best_frame_id} and byte position {best_byte} has the most linear relationship with an R-squared of {best_r_squared:.2f}")

        for action, data in self.found_action_frames.items():
            for idx, frame in enumerate(self.variable_frames_copy):
                if frame.id == data[0]:
                    self.table_reference[action] = [idx, self.found_action_frames[action][1]]
        print(self.table_reference)

        self.findFramesButton.hide()
        self.throttleLabel.show()
        self.brakeLabel.show()
        self.steeringLabel.show()

    def train_pipeline(self):
        output_file = 'data/combined_file.csv'
        # List to hold dataframes
        dfs = []

        # Read each CSV file and append to list
        for file_path in self.file_paths.keys():
            df = pd.read_csv(file_path)
            dfs.append(df)

        # Concatenate all dataframes in the list
        combined_df = pd.concat(dfs, ignore_index=True)

        # Write the combined dataframe to a new CSV file
        combined_df.to_csv(output_file, index=False)
        print(f"Combined CSV created at: {output_file}")

        model, scaler, label_encoder = model_train.train(self.frame_count)
        self.predictor = RealTimePredictor(model, scaler, label_encoder)
        self.loadButton.show()
        self.trainButton.hide()
        self.simulationControlWindow.state_label.show()

    def start_predict_pipeline(self):
        # Capture for period of duration
        predict_thread = threading.Thread(target=self.predict_pipeline)
        predict_thread.start()

    def predict_pipeline(self):
        while True:
            self.capture(1)
            # print(self.predictor.predict(self.captured_can_frames))
            self.simulationControlWindow.state_label.setText(self.predictor.predict(self.captured_can_frames,
                                                                                    self.frame_count))
            self.captured_can_frames = []
            time.sleep(0.001)

    def capture(self, duration, save=False):
        iteration = 0
        while iteration < duration:
            for frame_list in [self.variable_frames_copy, self.static_frames]:
                for obj in frame_list:
                    id_value = obj.id  # Ensure this is the correct attribute
                    data_value = obj.data  # Ensure this is the correct attribute
                    time.sleep(0.001)
                    timestamp_value = round(time.time(), 5)  # Current time

                    new_obj = {
                        "id": id_value,
                        "data": data_value,
                        "timestamp": timestamp_value,
                        "action": self.capture_mode
                    }
                    self.captured_can_frames.append(new_obj)
            iteration += 1

        if save:
            # Dump data into CSV file
            csv_file_path = f"data/{self.capture_mode}_data.csv"
            fieldnames = ['id', 'data', 'timestamp', 'action']  # Column headers for CSV
            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for data in self.captured_can_frames:
                    writer.writerow(data)

            self.captured_can_frames = []
            print(f"CSV file '{csv_file_path}' created successfully.")

    def enable_capture(self):
        sender = self.sender().objectName()
        print(f"The button '{sender}' was clicked.")
        self.capture_mode = sender[len("capture"):-len("Button")]
        print(self.capture_mode)

        # Initialize capture state from (1) for non-idle actions
        if self.capture_mode in self.capture_map:
            self.capture_map[self.capture_mode][1](self.capture_map[self.capture_mode][0])
        else:
            print("No function found for the keyword:", self.capture_mode)

        # Capture for period of duration
        capture_thread = threading.Thread(target=self.capture, args=(self.DEFAULT_DURATION, True))
        capture_thread.start()

        # Disable the pressed button
        if self.capture_mode in self.capture_states:
            self.capture_states[self.capture_mode](False)

        # Hide all buttons if all were clicked
        if all(not button.isEnabled() for button in
               [self.captureIdleButton, self.captureThrottleButton, self.captureBrakeButton,
                self.captureSteerRightButton,
                self.captureSteerLeftButton]):
            self.captureIdleButton.hide()
            self.captureThrottleButton.hide()
            self.captureBrakeButton.hide()
            self.captureSteerRightButton.hide()
            self.captureSteerLeftButton.hide()
            self.trainButton.show()
            self.findFramesButton.show()

    def set_steering_byte(self):
        """Calculate and update steering byte based on the slider value."""
        value = self.simulationControlWindow.steering_slider.value()
        if value == 127:
            self.steering_byte = ['00', '00']
        else:
            scaled_value = abs((value - 128) * 254 // (255 - 128) + 1)
            if value > 127:
                self.steering_byte = ['00', format(scaled_value, '02x')]
            else:
                self.steering_byte = [format(scaled_value, '02x'), '00']

    def set_brake_byte(self):
        """Set the brake byte from the brake slider's value."""
        value = self.simulationControlWindow.brake_slider.value()
        self.brake_byte = format(value, '02x')

    def set_throttle_byte(self):
        """Set the throttle byte from the throttle slider's value."""
        value = self.simulationControlWindow.throttle_slider.value()
        self.throttle_byte = format(value, '02x')

    def update_byte(self, byte_name, frame_idx, byte_idx):
        """General method to update a byte in a frame."""
        getattr(self, f"set_{byte_name}_byte")()
        frame = self.variable_frames_copy[frame_idx]
        data = frame.data
        byte = getattr(self, f"{byte_name}_byte")
        frame.data = data[:byte_idx] + byte + data[byte_idx + 2:]

    def update_steering_bytes(self):
        """Update the bytes for steering, handling multiple indices."""
        self.set_steering_byte()
        frame = self.variable_frames_copy[self.steering_frame_idx]
        data = frame.data
        replacements = {self.steering_byte_idx[0]: self.steering_byte[0],
                        self.steering_byte_idx[1]: self.steering_byte[1]}
        parts = [data[:min(replacements.keys())]]
        sorted_indices = sorted(replacements.keys())

        for i, idx in enumerate(sorted_indices):
            parts.append(replacements[idx])
            next_part_start = idx + 2
            if i + 1 < len(sorted_indices):
                next_idx = sorted_indices[i + 1]
                parts.append(data[next_part_start:next_idx])
            else:
                parts.append(data[next_part_start:])

        frame.data = ''.join(parts)

    def update_variable_bytes(self):
        """Update variable bytes for throttle, brake, and steering."""
        self.update_byte('throttle', self.throttle_frame_idx, self.throttle_byte_idx)
        self.update_byte('brake', self.brake_frame_idx, self.brake_byte_idx)
        self.update_steering_bytes()

    def simulate_variable_frames(self):
        for frame in self.chosen_variable_frames:
            self.update_variable_bytes()
            self.variable_frames_copy[frame.idx].data = random.choice(frame.random_hex_numbers)

            self.clear_table()
            self.generate_table(self.variable_frames_copy + self.static_frames)

            # Colour the found action frames
            if self.found_action_frames:
                for action, (frame_id, byte_position, r_squared) in self.found_action_frames.items():
                    color = self.get_color_for_action(action)
                    self.color_cells(frame_id, byte_position, color)

    def generate_fixed_hex(self, num_of_random_hex):
        # random.seed(self.RANDOM_SEED)
        # Calculate the number of bytes the hex number should have
        num_bytes = 8  # Each byte is represented by two hex characters
        for frame in self.chosen_variable_frames:
            for _ in range(random.randint(2, num_of_random_hex)):
                # Generate a random integer with the right number of bits (8 bits per byte)
                random_int = random.getrandbits(num_bytes * 8)
                # Convert integer to a hexadecimal string, and format to ensure correct length
                random_hex = format(random_int, '0{}x'.format(num_bytes * 2))
                # Append the formatted hex string to the list
                frame.random_hex_numbers.append(random_hex)

    def generate_variable_byte_idx(self, flag=0):
        """
            Generate indices for variable bytes within a 16-byte frame.
            Depending on the flag, return either a single index or a pair of indices.
        """
        random.seed(self.RANDOM_SEED)
        even_indices = list(range(0, 16, 2))
        if flag == 1:
            return random.sample(even_indices, 2)
        return random.choice(even_indices)

    def generate_variable_frames(self):
        """
        Randomly assigns indices to throttle, brake, steering, and other variable frames
        from the available list of frames.
        """
        random.seed(self.RANDOM_SEED)
        # Create a list of indices based on the number of variable frames available
        frames = list(range(len(self.variable_frames)))

        random.shuffle(frames)

        # Unpack the first three indices for throttle, brake, and steering controls
        self.throttle_frame_idx, self.brake_frame_idx, self.steering_frame_idx = frames[:3]

        # The rest of the indices are assigned to general variable frames
        self.variable_frames_idx = frames[3:]

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
        """
        Formats and adds rows to a table for a list of frames. Each frame's data
        is displayed across 9 columns: one for the frame ID and eight for the data bytes.

        Args:
            frames (list): A list of frame objects, where each frame has 'id' and 'data' attributes.

        """
        for frame in frames:
            # Start each row with the frame's ID, formatted as a hex string
            data_row = ["0x" + frame.id]

            # Add each byte of the frame's data to the row, also formatted as hex
            for i in range(0, len(frame.data), 2):  # Process two characters at a time for hex byte representation
                data_row.append("0x" + frame.data[i:i + 2])

            # Create a copy of the current row to add to the table
            data_row_copy = data_row.copy()
            self.add_row(data_row_copy)

    def split_frames(self, ratio=0.6):
        random.seed(self.RANDOM_SEED)
        random.shuffle(self.frames)

        split_index = int(len(self.frames) * ratio)

        self.variable_frames = self.frames[:split_index]
        self.static_frames = self.frames[split_index:]

    def generate_frames(self, frame_count):
        random.seed(self.RANDOM_SEED)
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
        """Starts the simulation based on user-defined parameters and prepares the simulation environment."""
        print("Simulation start")

        # Request the user to specify the number of frames to simulate
        self.frame_count = self.open_input_dialog()

        # Generate and split frames based on the specified count
        self.generate_frames(self.frame_count)
        self.split_frames()  # Splits frames into variable and static frames with a ratio of 0.6 to 0.4
        self.variable_frames_copy = self.variable_frames.copy()

        # Generate the display table for the frames
        self.generate_table(self.frames)
        self.startButton.hide()  # Disable the start button after the simulation starts
        self.captureIdleButton.setEnabled(True)
        self.captureThrottleButton.setEnabled(True)
        self.captureBrakeButton.setEnabled(True)
        self.captureSteerRightButton.setEnabled(True)
        self.captureSteerLeftButton.setEnabled(True)

        # Generate indices for specific control frames and others
        self.generate_variable_frames()

        # Create VariableFrame objects using indices from the variable frames
        self.chosen_variable_frames = [
            VariableFrame(self.variable_frames[i].id, self.variable_frames[i].data, i)
            for i in self.variable_frames_idx
        ]

        # Generate and configure fixed hex values for variable frames
        self.generate_fixed_hex(5)

        # Generate indices for specific byte modifications in throttle, brake, and steering controls
        self.throttle_byte_idx = self.generate_variable_byte_idx()
        self.brake_byte_idx = self.generate_variable_byte_idx()
        self.steering_byte_idx = self.generate_variable_byte_idx(1)

        # Start the variable frames timer to trigger updates
        self.variable_frames_timer.start(50)  # Timer set to trigger every 50 milliseconds

        # Show the controls window and indicate the simulation is fully configured
        self.simulationControlWindow.show()

        print("Simulation setup complete and running.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PrimaryWindow()
    window.show()
    sys.exit(app.exec())
