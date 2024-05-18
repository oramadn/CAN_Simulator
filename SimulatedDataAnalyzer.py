import sys
import random
import csv
import threading
import time
import pandas as pd

from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
                               QTableWidgetItem, QLabel, QInputDialog, QGridLayout, QComboBox)
from PySide6.QtCore import QTimer, QMimeData, Qt
from PySide6.QtGui import QColor, QDrag, QDragEnterEvent

from frame_generator import generate_random_frames
from SimulationControlWindow import SimulationControl
from linear_map_frame import analyze_linear_relationship_per_frame
import model_train
from realtime_predictor import RealTimePredictor
from gadgets.GaugeGadget import GaugeWidget
from gadgets.LCDGadget import LCDWidget
from gadgets.VerticalBarGadget import VerticalBarWidget

RANDOM_SEED = 21
CAPTURE_ITERATION = 500


class DataTable(QTableWidget):
    def __init__(self):
        super().__init__(0, 9)  # Initialize with 0 rows and 9 columns
        self.setHorizontalHeaderLabels(['ID', '0', '1', '2', '3', '4', '5', '6', '7'])
        self.setColumnWidth(0, 100)  # Wider column for ID
        for i in range(1, 9):
            self.setColumnWidth(i, 30)  # Set the width for byte columns
        self.setFixedWidth(460)
        self.setMinimumHeight(550)

        self.setDragEnabled(True)
        self.observers = []  # List to track which IDs are being observed

    def populate_table(self, frames, found_action_frames):
        """Fill the table with the data in frames."""
        self.frames = frames
        self.setRowCount(len(frames))
        for row, frame in enumerate(frames):
            # Set the ID in the first column
            self.setItem(row, 0, QTableWidgetItem(frame['id']))

            data = frame['data']
            # Populate each byte into its corresponding column
            for col in range(1, 9):  # Columns 1 through 8 for bytes 0 through 7
                if len(data) >= col * 2:  # Check if there is enough data for this byte
                    byte = data[(col - 1) * 2:(col - 1) * 2 + 2]  # Extract the byte
                    cell_item = QTableWidgetItem(byte)
                    self.setItem(row, col, cell_item)

                    # Check if this byte should be colored based on found_action_frames
                    for action_frame in found_action_frames:
                        if action_frame['id'] == frame['id'] and action_frame['byte_idx'] == col - 1:
                            color = self.get_color_by_label(action_frame['label'])
                            cell_item.setBackground(color)
                else:
                    # If there is no data for this byte, set an empty string
                    self.setItem(row, col, QTableWidgetItem(''))

    def get_color_by_label(self, label):
        """Return QColor based on the label."""
        if label == 'throttle':
            return QColor(125, 40, 40)  # Dark Red
        elif label == 'brake':
            return QColor(55, 78, 161)  # Blue
        elif label == 'steerLeft' or label == 'steerRight':
            return QColor(90, 166, 95)  # Green
        return QColor(255, 255, 255)  # Default to white if no match

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()
        drag = QDrag(self)
        mimeData.setText(self.currentItem().text())  # Assuming the drag initiates from the ID column
        drag.setMimeData(mimeData)
        drag.exec(Qt.CopyAction)


class DataGadgets(QWidget):
    def __init__(self, get_current_frames):
        super().__init__()
        self.get_current_frames = get_current_frames
        self.setFixedSize(200, 240)
        self.main_layout = QVBoxLayout(self)
        self.current_id = None
        self.current_byte_idx = None
        self.byteComboBoxConnected = False  # Flag to track connection status
        self.current_gadget = None  # To hold the current gadget

        # Initial dropdown to select the type of gadget
        self.init_gadget_selector()

        # Label for displaying the selected ID
        self.label = QLabel("Choose a gadget")
        self.main_layout.addWidget(self.label)

        # Timer to update the label every 50ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)

    def init_gadget_selector(self):
        self.gadget_selector = QComboBox()
        self.gadget_selector.addItem("None", None)  # Default
        self.gadget_selector.addItem("Gauge", ('GaugeWidget', 0, 255))
        self.gadget_selector.addItem("LCD Screen", ('LCDWidget', None, None))
        self.gadget_selector.addItem("Bar", ('VerticalBarWidget', None, None))
        self.gadget_selector.currentIndexChanged.connect(self.gadget_selected)
        self.main_layout.addWidget(self.gadget_selector, 0, Qt.AlignHCenter)

    def gadget_selected(self, index):
        item_data = self.gadget_selector.itemData(index)
        if item_data:
            gadget_type, min_val, max_val = item_data
            if self.current_gadget:
                self.main_layout.removeWidget(self.current_gadget)
                self.current_gadget.deleteLater()

            self.label.setVisible(False)  # Hide label as a gadget is selected

            if gadget_type == "GaugeWidget":
                self.current_gadget = GaugeWidget(min_val, max_val)
                self.current_gadget.setFixedSize(150, 150)
            elif gadget_type == "LCDWidget":
                self.current_gadget = LCDWidget()
            elif gadget_type == "VerticalBarWidget":
                self.current_gadget = VerticalBarWidget()

            if self.current_gadget:
                self.main_layout.insertWidget(1, self.current_gadget, alignment=Qt.AlignCenter)  # Insert the gadget at position 1
                self.init_byte_selector()

        else:  # In case "None" is selected
            self.label.setVisible(True)

    def init_byte_selector(self):
        if not hasattr(self, 'byte_selector'):
            self.byte_layout = QHBoxLayout()
            label = QLabel("Byte:")
            self.byte_selector = QComboBox()
            self.byte_selector.addItem("None", None)
            for i in range(8):
                self.byte_selector.addItem(str(i), i)

            self.byte_layout.addWidget(label)
            self.byte_layout.addWidget(self.byte_selector)
            self.byte_selector.currentIndexChanged.connect(self.byte_combobox_triggered)

        # Ensure the byte selector is always at the bottom of all widgets
        if self.byte_layout not in self.main_layout.children():
            self.main_layout.addLayout(self.byte_layout)
        self.setAcceptDrops(True)

    def byte_combobox_triggered(self, byte_index):
        self.current_byte_idx = byte_index
        self.timer.start(50)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        new_id = event.mimeData().text()
        if new_id:
            if len(new_id) == 2:
                self.label.setText("Please insert an ID only!")
            else:
                self.current_id = new_id
                self.update_display()
                self.label.setText(f"Selected ID: {self.current_id}")

    def update_display(self):
        if self.current_id and self.current_byte_idx is not None:
            data = self.find_data_by_id()
            if data:
                hex_data = data[self.current_byte_idx * 2:(self.current_byte_idx * 2) + 2]
                self.current_gadget.set_value(int(hex_data, 16))

    def find_data_by_id(self):
        frames = self.get_current_frames()
        for frame in frames:
            if frame['id'] == self.current_id:
                return frame['data']


class DataControls(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        button = QPushButton("Test")
        layout.addWidget(button)
        self.setLayout(layout)


class DataPlotter(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Plotters based on Data")
        layout.addWidget(label)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN Analyzer")
        self.file_paths = {
            'idle': 'data/idle_data.csv',
            'throttle': 'data/throttle_data.csv',
            'brake': 'data/brake_data.csv',
            'steerLeft': 'data/steerLeft_data.csv',
            'steerRight': 'data/steerRight_data.csv'
        }
        self.found_action_frames = []
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)

        self.top_layout = QHBoxLayout()
        self.findFramesButton = QPushButton("Find frames")
        self.trainButton = QPushButton("Train model")
        self.predictButton = QPushButton("Load trained model")
        self.top_layout.addWidget(self.findFramesButton)
        self.top_layout.addWidget(self.trainButton)
        self.top_layout.addWidget(self.predictButton)

        content_layout = QHBoxLayout()
        table_layout = QVBoxLayout()
        self.table = DataTable()
        self.controls = DataControls()
        table_layout.addWidget(self.table)
        table_layout.addWidget(self.controls)
        content_layout.addLayout(table_layout)

        right_layout = QVBoxLayout()

        top_right_layout = QGridLayout()
        self.gadgets = []  #

        for row in range(2):
            row_list = []  # List to hold gadgets for this row
            for col in range(3):
                gadget = DataGadgets(self.get_current_frames)
                top_right_layout.addWidget(gadget, row, col)
                row_list.append(gadget)
            self.gadgets.append(row_list)

        bottom_right_layout = QVBoxLayout()
        plotter = DataPlotter()
        bottom_right_layout.addWidget(plotter)

        right_layout.addLayout(top_right_layout)
        right_layout.addLayout(bottom_right_layout)

        content_layout.addLayout(right_layout)

        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addLayout(content_layout)

        self.setup_control_ui()
        self.setup_simulation()

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

    def setup_control_ui(self):
        self.sim_control = SimulationControl()
        self.sim_control.captureIdleButton.clicked.connect(lambda: self.enable_capture("idle"))
        self.sim_control.captureThrottleButton.clicked.connect(lambda: self.enable_capture("throttle"))
        self.sim_control.captureBrakeButton.clicked.connect(lambda: self.enable_capture("brake"))
        self.sim_control.captureSteerLeftButton.clicked.connect(lambda: self.enable_capture("steerLeft"))
        self.sim_control.captureSteerRightButton.clicked.connect(lambda: self.enable_capture("steerRight"))

        self.capture_button_enable = {
            'idle': self.sim_control.captureIdleButton.setEnabled,
            'throttle': self.sim_control.captureThrottleButton.setEnabled,
            'brake': self.sim_control.captureBrakeButton.setEnabled,
            'steerLeft': self.sim_control.captureSteerLeftButton.setEnabled,
            'steerRight': self.sim_control.captureSteerRightButton.setEnabled
        }
        self.sim_control.state_label.hide()

        self.sim_control.show()

    def setup_simulation(self):
        self.frame_count = self.open_input_dialog()
        if self.frame_count == 0:
            exit()

        self.initial_frames = generate_random_frames(self.frame_count, 5, 0.5, RANDOM_SEED)
        self.throttleFrame, self.brakeFrame, self.steeringFrame = self.initial_frames[0], self.initial_frames[1], \
            self.initial_frames[2]

        self.assign_random_byte_for_action(self.throttleFrame)
        self.assign_random_byte_for_action(self.brakeFrame)
        self.assign_random_byte_for_action(self.steeringFrame, 2)

        self.initial_frames = sorted(self.initial_frames, key=lambda x: int(x['id'], 16))

        self.findFramesButton.clicked.connect(self.find_action_frames)  # REMOVE IN FINAL VERSION
        self.trainButton.clicked.connect(self.train_model)  # REMOVE IN FINAL VERSION
        self.predictButton.clicked.connect(self.start_predict)  # REMOVE IN FINAL VERSION

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate)
        self.timer.start(50)

    def assign_random_byte_for_action(self, frame, num_bytes=1):
        random.seed(RANDOM_SEED)
        even_indices = list(range(0, len(frame['data']), 2))
        selected_indices = random.sample(even_indices, num_bytes)
        selected_bytes = [frame['data'][idx:idx + 2] for idx in selected_indices]
        for idx in selected_indices:
            new_data = frame['data'][:idx] + '00' + frame['data'][idx + 2:]
            frame['data'] = new_data
        frame['byte'] = selected_bytes
        frame['byte idx'] = selected_indices

    def simulate(self):
        self.update_throttle_byte()
        self.update_brake_byte()
        self.update_steering_byte()
        self.frames = self.update_frames()
        self.table.populate_table(self.frames, self.found_action_frames)

    def get_current_frames(self):
        return self.frames

    def get_throttle_slider_value(self):
        return self.sim_control.throttle_slider.value()

    def get_brake_slider_value(self):
        return self.sim_control.brake_slider.value()

    def get_steering_slider_value(self):
        return self.sim_control.steering_slider.value()

    def update_throttle_byte(self):
        byte = format(self.get_throttle_slider_value(), '02X')
        frame = self.throttleFrame['data']
        idx = self.throttleFrame['byte idx'][0]
        new_data = frame[:idx] + byte + frame[idx + 2:]
        self.throttleFrame['data'] = new_data

    def update_brake_byte(self):
        byte = format(self.get_brake_slider_value(), '02X')
        frame = self.brakeFrame['data']
        idx = self.brakeFrame['byte idx'][0]
        new_data = frame[:idx] + byte + frame[idx + 2:]
        self.brakeFrame['data'] = new_data

    def update_steering_byte(self):
        frame = self.steeringFrame['data']
        idx = self.steeringFrame['byte idx']
        byte = self.get_steering_slider_value()
        if byte == 127:
            new_data = frame[:idx[0]] + '00' + frame[idx[0] + 2:]
            new_data = new_data[:idx[1]] + '00' + new_data[idx[1] + 2:]
        else:
            scaled_byte = abs((byte - 128) * 254 // (255 - 128) + 1)
            if byte > 127:
                new_data = frame[:idx[0]] + '00' + frame[idx[0] + 2:]
                new_data = new_data[:idx[1]] + format(scaled_byte, '02X') + new_data[idx[1] + 2:]
            else:
                new_data = frame[:idx[0]] + format(scaled_byte, '02X') + frame[idx[0] + 2:]
                new_data = new_data[:idx[1]] + '00' + new_data[idx[1] + 2:]
        self.steeringFrame['data'] = new_data

    def update_frames(self):
        """Update self.frames with randomly selected data if multiple options exist."""
        new_frames = []
        for frame in self.initial_frames:
            data = frame['data']
            # Select a random data frame if there are multiple
            if isinstance(data, list):
                data = random.choice(data)
            new_frames.append({'id': frame['id'], 'data': data})
        return new_frames

    def enable_capture(self, button_name):
        print(f"Capture triggered by: {button_name}")

        # Disable the pressed button
        if button_name in self.capture_button_enable:
            self.capture_button_enable[button_name](False)

        # Hide all buttons if all were clicked
        if all(not button.isEnabled() for button in
               [self.sim_control.captureIdleButton, self.sim_control.captureThrottleButton,
                self.sim_control.captureBrakeButton,
                self.sim_control.captureSteerLeftButton,
                self.sim_control.captureSteerRightButton]):
            self.sim_control.captureIdleButton.hide()
            self.sim_control.captureThrottleButton.hide()
            self.sim_control.captureBrakeButton.hide()
            self.sim_control.captureSteerRightButton.hide()
            self.sim_control.captureSteerLeftButton.hide()

            # self.findFramesButton.clicked.connect(self.find_action_frames())
            # self.trainButton.clicked.connect(self.train_model)
            # self.predictButton.clicked.connect(self.start_predict)
            # self.findFramesButton.show()
            # self.trainButton.show()

        capture_thread = threading.Thread(target=self.capture,
                                          args=(CAPTURE_ITERATION, button_name, self.file_paths[button_name], True))
        capture_thread.start()

    def capture(self, iterations, label=None, file_path=None, save=False):
        data = []
        if save:
            for _ in range(iterations):
                for frame in self.frames:
                    data.append({
                        "id": frame['id'],
                        "data": frame['data'],
                        "label": label
                    })
                    time.sleep(0.001)
            self.save_to_csv(data, file_path)
        else:
            for _ in range(iterations):
                for frame in self.frames:
                    data.append({
                        "id": frame['id'],
                        "data": frame['data'],
                    })
                    time.sleep(0.001)
            return data

    def save_to_csv(self, data, file_path):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'data', 'label'])  # Write the header

            for item in data:
                writer.writerow([item["id"], item["data"], item["label"]])

        print(f"Successfully saved {file_path}")

    def find_action_frames(self):
        for label, file_path in self.file_paths.items():
            if file_path == "data/idle_data.csv":
                continue
            best_frame_id, best_byte, best_r_squared = analyze_linear_relationship_per_frame(file_path,
                                                                                             self.frame_count)
            self.found_action_frames.append({'label': label, 'id': best_frame_id, 'byte_idx': best_byte,
                                             'r_squared': best_r_squared})
            print(f"The {label} frame ID is {best_frame_id} and byte position {best_byte} has the most linear relationship with an R-squared of {best_r_squared:.2f}")

        self.findFramesButton.hide()

    def train_model(self):
        output_file = 'data/combined_file.csv'

        dfs = []
        for _, file_path in self.file_paths.items():
            df = pd.read_csv(file_path)
            dfs.append(df)
        combined_df = pd.concat(dfs, ignore_index=True)

        combined_df.to_csv(output_file, index=False)
        print(f"Combined CSV created at: {output_file}")

        model, scaler, label_encoder = model_train.train(self.frame_count)
        self.predictor = RealTimePredictor(model, scaler, label_encoder)
        self.predictButton.show()
        self.trainButton.hide()
        self.sim_control.state_label.show()

    def start_predict(self):
        # Capture for period of duration
        predict_thread = threading.Thread(target=self.predict)
        predict_thread.start()

    def predict(self):
        while True:
            frames = self.capture(1)
            self.sim_control.state_label.setText(self.predictor.predict(frames,
                                                                        self.frame_count))
            time.sleep(0.001)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
