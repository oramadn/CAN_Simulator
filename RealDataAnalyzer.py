import sys
import serial
import csv
import threading
import time
import pandas as pd

from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
                               QTableWidgetItem, QLabel, QInputDialog, QGridLayout, QComboBox, QSpacerItem, QSizePolicy,
                               QSlider, QLineEdit)
from PySide6.QtCore import QTimer, QMimeData, Qt
from PySide6.QtGui import QColor, QDrag

from linear_map_frame import analyze_linear_relationship_per_frame
import model_train
from realtime_predictor import RealTimePredictor
from gadgets.GaugeGadget import GaugeWidget
from gadgets.LCDGadget import LCDWidget
from gadgets.VerticalBarGadget import VerticalBarWidget
from gadgets.LineGraphGadget import LineChartWidget
from serial_read import serial_read

RANDOM_SEED = 25
CAPTURE_ITERATION = 100


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
        self.setFixedSize(400, 240)
        self.main_layout = QVBoxLayout(self)
        self.current_id = None
        self.current_byte_idx = None
        self.current_gadget = None
        self.byteComboBoxConnected = False  # Flag to track connection status

        # Label for displaying the selected ID
        self.gadget_label = QLabel("Choose a gadget")
        self.main_layout.addWidget(self.gadget_label, 0, Qt.AlignHCenter)

        # Initial dropdown to select the type of gadget
        self.init_gadget_selector()

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

        # Horizontal layout for the "Selected ID" and actual ID
        self.id_layout = QHBoxLayout()

        # Label for "Selected ID:"
        self.selected_id_label = QLabel("Selected ID:")
        self.id_layout.addWidget(self.selected_id_label, alignment=Qt.AlignLeft)

        # Spacer to push apart "Selected ID:" and the actual ID
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.id_layout.addItem(spacer)

        # Label for displaying the actual ID
        self.current_id_value = QLabel(self.current_id)
        self.id_layout.addWidget(self.current_id_value, alignment=Qt.AlignRight)

        # Add the ID layout to the main layout
        self.main_layout.addLayout(self.id_layout)

        self.selected_id_label.setVisible(False)
        self.current_id_value.setVisible(False)

        # Set the window's main layout
        self.setLayout(self.main_layout)

    def gadget_selected(self, index):
        item_data = self.gadget_selector.itemData(index)
        if item_data:
            gadget_type, min_val, max_val = item_data
            if self.current_gadget:
                self.main_layout.removeWidget(self.current_gadget)
                self.current_gadget.deleteLater()

            self.gadget_label.setVisible(False)  # Hide label as a gadget is selected

            if gadget_type == "GaugeWidget":
                self.current_gadget = GaugeWidget(min_val, max_val)
                self.current_gadget.setFixedSize(150, 150)
            elif gadget_type == "LCDWidget":
                self.current_gadget = LCDWidget()
            elif gadget_type == "VerticalBarWidget":
                self.current_gadget = VerticalBarWidget()

            if self.current_gadget:
                self.main_layout.insertWidget(1,
                                              self.current_gadget,
                                              alignment=Qt.AlignCenter)  # Insert the gadget at position 1
                self.init_byte_selector()

                self.main_layout.removeWidget(self.gadget_selector)
                self.main_layout.insertWidget(2, self.gadget_selector, 0, Qt.AlignLeft)

        else:  # In case "None" is selected
            self.gadget_label.setVisible(True)

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

        self.selected_id_label.setVisible(True)
        self.current_id_value.setVisible(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        new_id = event.mimeData().text()
        if new_id:
            if len(new_id) == 2:
                self.current_id_value.setText("Insert an ID only!")
            else:
                self.current_id = new_id
                self.update_display()
                self.current_id_value.setText(self.current_id)

    def byte_combobox_triggered(self, byte_index):
        self.current_byte_idx = byte_index
        self.timer.start(50)

    def update_display(self):
        if self.current_id and self.current_byte_idx is not None:
            data = self.find_data_by_id()
            if data:
                hex_data = data[(self.current_byte_idx - 1) * 2:(
                                                                        self.current_byte_idx - 1) * 2 + 2]  # -1 since actual idx starts at 1 becuase None was added as an option
                self.current_gadget.set_value(int(hex_data, 16))

    def find_data_by_id(self):
        frames = self.get_current_frames()
        for frame in frames:
            if frame['id'] == self.current_id:
                return frame['data']


class DataControls(QWidget):
    def __init__(self, set_current_frames):
        super().__init__()
        self.setFixedWidth(230)
        self.main_layout = QVBoxLayout(self)
        self.setAcceptDrops(True)

        self.current_id = None
        self.current_byte_idx = None
        self.set_current_frames = set_current_frames

        # Label to instruct user or show selected ID
        self.id_label = QLabel("Drag and drop an ID here")
        self.main_layout.addWidget(self.id_label, 0, Qt.AlignHCenter)

        # Combo box to select control type
        self.control_selector = QComboBox()
        self.control_selector.addItem("Select control", None)
        self.control_selector.addItem("Slider", "slider")
        self.control_selector.addItem("Input Field", "input")
        self.control_selector.currentIndexChanged.connect(self.control_selected)
        self.control_selector.setVisible(False)
        self.main_layout.addWidget(self.control_selector, 1, Qt.AlignHCenter)

        # Byte Selector
        self.byte_selector = QComboBox()
        self.byte_selector.addItem("Select Byte", None)
        for i in range(8):
            self.byte_selector.addItem(f"Byte {i}", i)
        self.byte_selector.currentIndexChanged.connect(self.byte_selected)
        self.byte_selector.setVisible(False)
        self.main_layout.addWidget(self.byte_selector)

        # Placeholder for control widget
        self.control_widget = None
        self.input_submit_button = None  # Button for submitting input field value

    def control_selected(self, index):
        # Remove the old widget and button if any
        if self.control_widget:
            self.main_layout.removeWidget(self.control_widget)
            self.control_widget.deleteLater()
            self.control_widget = None
        if self.input_submit_button:
            self.main_layout.removeWidget(self.input_submit_button)
            self.input_submit_button.deleteLater()
            self.input_submit_button = None

        control_type = self.control_selector.itemData(index)
        if control_type == "slider":
            self.control_widget = QSlider(Qt.Horizontal)
            self.control_widget.setMinimum(0)
            self.control_widget.setMaximum(255)
            self.control_widget.valueChanged.connect(self.slider_value_changed)
            self.main_layout.addWidget(self.control_widget, 2, Qt.AlignHCenter)
        elif control_type == "input":
            self.control_widget = QLineEdit()
            self.control_widget.setPlaceholderText("Enter value")
            self.input_submit_button = QPushButton("Submit")
            self.input_submit_button.clicked.connect(self.input_value_submitted)
            layout = QHBoxLayout()
            layout.addWidget(self.control_widget)
            layout.addWidget(self.input_submit_button)
            self.main_layout.addLayout(layout, 2)

    def byte_selected(self, index):
        self.current_byte_idx = self.byte_selector.itemData(index)
        if self.current_byte_idx is not None:
            print(f"Byte {self.current_byte_idx} selected")

    def slider_value_changed(self, value):
        if self.current_id and self.current_byte_idx is not None:
            hex_value = f"{value:02x}"
            self.set_current_frames(self.current_id, self.current_byte_idx, hex_value)

    def input_value_submitted(self):
        if self.control_widget and self.current_id and self.current_byte_idx is not None:
            value = self.control_widget.text()
            try:
                int_value = int(value)
                if 0 <= int_value <= 255:
                    hex_value = f"{int_value:02x}"
                    self.set_current_frames(self.current_id, self.current_byte_idx, hex_value)
                else:
                    self.control_widget.setText("Invalid value")
            except ValueError:
                self.control_widget.setText("Invalid input")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        id_text = event.mimeData().text()
        if id_text:
            if len(id_text) == 2:
                self.id_label.setText("Please insert a full ID!")
            else:
                self.current_id = id_text
                self.id_label.setText(f"Selected ID: {self.current_id}")
                self.control_selector.setVisible(True)
                self.byte_selector.setVisible(True)


class DataPlotter(QWidget):
    def __init__(self, get_current_frames):
        super().__init__()
        self.get_current_frames = get_current_frames
        self.main_layout = QVBoxLayout(self)
        self.current_id = None
        self.current_byte_idx = None
        self.current_plotter = None
        self.byte_selector = None

        self.selected_id_label = QLabel("Drop ID to plot")
        self.main_layout.addWidget(self.selected_id_label, 0, Qt.AlignHCenter)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        new_id = event.mimeData().text()
        if len(new_id) != 2:  # Assuming IDs are longer than 2 characters
            self.current_id = new_id
            self.init_plotter()  # Initialize the plotter with the title of the selected ID
            self.init_byte_selector()
            self.selected_id_label.deleteLater()  # Remove the label after the ID is dropped

    def init_plotter(self):
        if self.current_plotter:  # Reset if there's an existing plotter
            self.main_layout.removeWidget(self.current_plotter)
            self.current_plotter.deleteLater()

        self.current_plotter = LineChartWidget()
        self.current_plotter.setFixedSize(400, 350)  # Set the fixed size for the plotter
        self.current_plotter.chart.setTitle(f"Selected ID: {self.current_id}")  # Set the title with the current ID
        self.main_layout.addWidget(self.current_plotter, 1, Qt.AlignHCenter)  # Add the plotter to the layout

    def init_byte_selector(self):
        if self.byte_selector:  # Clear the existing byte selector if any
            self.main_layout.removeWidget(self.byte_selector)
            self.byte_selector.deleteLater()

        self.byte_selector = QComboBox()
        self.byte_selector.addItem("Select Byte", None)  # Default prompt item
        for i in range(8):  # Assuming bytes 0-7
            self.byte_selector.addItem(str(i), i)

        self.byte_selector.currentIndexChanged.connect(self.byte_combobox_triggered)
        self.main_layout.addWidget(self.byte_selector, 2, Qt.AlignHCenter)  # Position after the plotter

    def byte_combobox_triggered(self, index):
        if index > 0:  # Ensure it's not the default prompt
            self.current_byte_idx = self.byte_selector.itemData(index)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_display)
            self.timer.start(50)  # Update every second

    def update_display(self):
        if self.current_id and self.current_byte_idx is not None:
            data = self.find_data_by_id()
            if data:
                hex_data = data[self.current_byte_idx * 2:(self.current_byte_idx * 2) + 2]
                self.current_plotter.set_value(int(hex_data, 16))

    def find_data_by_id(self):
        frames = self.get_current_frames()
        for frame in frames:
            if frame['id'] == self.current_id:
                return frame['data']


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN Analyzer")
        self.resize(1920, 1000)
        self.file_paths = {
            'idle': 'data/idle_data.csv',
            'throttle': 'data/throttle_data.csv',
            'brake': 'data/brake_data.csv',
            'steerLeft': 'data/steerLeft_data.csv',
            'steerRight': 'data/steerRight_data.csv'
        }
        self.frames = []
        self.found_action_frames = []
        self.run_predict = False
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)

        content_layout = QHBoxLayout()

        self.table_layout = QVBoxLayout()

        # Capturing buttons
        self.button_layout = QHBoxLayout()
        self.setup_buttons()

        # Table
        self.table = DataTable()

        # Controllers layout
        controllers_layout = QGridLayout()
        self.controllers = []

        for row in range(3):
            row_list = []
            for col in range(2):
                controller = DataControls(self.set_current_frames)
                controllers_layout.addWidget(controller, row, col)
                row_list.append(controller)
            self.controllers.append(row_list)

        self.table_layout.addLayout(self.button_layout)
        self.table_layout.addWidget(self.table)
        self.table_layout.addLayout(controllers_layout)

        # content_layout.addLayout(self.button_layout)
        content_layout.addLayout(self.table_layout)

        right_layout = QVBoxLayout()

        # Gadgets layout
        top_right_layout = QGridLayout()
        self.gadgets = []

        for row in range(2):
            row_list = []
            for col in range(3):
                gadget = DataGadgets(self.get_current_frames)
                top_right_layout.addWidget(gadget, row, col)
                row_list.append(gadget)
            self.gadgets.append(row_list)

        # Plotters layout
        bottom_right_layout = QHBoxLayout()
        bottom_right_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.plotters = []

        for plot in range(3):
            plotter = DataPlotter(self.get_current_frames)
            bottom_right_layout.addWidget(plotter)
            bottom_right_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self.plotters.append(plotter)

        right_layout.addLayout(top_right_layout)
        right_layout.addLayout(bottom_right_layout)

        content_layout.addLayout(right_layout)

        self.main_layout.addLayout(content_layout)

        self.setup_simulation()

    def setup_buttons(self):
        # Control buttons
        self.recordButton = QPushButton("Start recording")
        self.recordButton.clicked.connect(self.enable_recording_buttons)
        self.trainButton = QPushButton("Train model")
        self.findFramesButton = QPushButton("Find frames")
        self.starPredictButton = QPushButton("Start predicting")
        self.stopPredictButton = QPushButton("Stop predicting")
        self.button_layout.addWidget(self.recordButton)
        self.button_layout.addWidget(self.trainButton)
        self.button_layout.addWidget(self.findFramesButton)
        self.button_layout.addWidget(self.starPredictButton)
        self.button_layout.addWidget(self.stopPredictButton)
        self.trainButton.hide()
        self.findFramesButton.hide()
        self.starPredictButton.hide()
        self.stopPredictButton.hide()

        # Capture buttons
        self.captureIdleButton = QPushButton("Record Idle")
        self.captureThrottleButton = QPushButton("Record Throttle")
        self.captureBrakeButton = QPushButton("Record Brake")
        self.captureSteerRightButton = QPushButton("Record Steer Right")
        self.captureSteerLeftButton = QPushButton("Record Steer Left")
        self.button_layout.addWidget(self.captureIdleButton)
        self.button_layout.addWidget(self.captureThrottleButton)
        self.button_layout.addWidget(self.captureBrakeButton)
        self.button_layout.addWidget(self.captureSteerRightButton)
        self.button_layout.addWidget(self.captureSteerLeftButton)

        self.captureIdleButton.clicked.connect(lambda: self.enable_capture("idle"))
        self.captureThrottleButton.clicked.connect(lambda: self.enable_capture("throttle"))
        self.captureBrakeButton.clicked.connect(lambda: self.enable_capture("brake"))
        self.captureSteerLeftButton.clicked.connect(lambda: self.enable_capture("steerLeft"))
        self.captureSteerRightButton.clicked.connect(lambda: self.enable_capture("steerRight"))

        self.capture_button_enable = {
            'idle': self.captureIdleButton.setEnabled,
            'throttle': self.captureThrottleButton.setEnabled,
            'brake': self.captureBrakeButton.setEnabled,
            'steerLeft': self.captureSteerLeftButton.setEnabled,
            'steerRight': self.captureSteerRightButton.setEnabled
        }

        self.captureIdleButton.hide()
        self.captureThrottleButton.hide()
        self.captureBrakeButton.hide()
        self.captureSteerRightButton.hide()
        self.captureSteerLeftButton.hide()

    def setup_simulation(self):
        # Configure the serial port
        self.ser = serial.Serial('COM4', 1000000, timeout=1)
        self.ser.reset_input_buffer()

        # Wait for the serial connection to initialize
        time.sleep(2)

        serial_thread = threading.Thread(target=self.serial_read)
        serial_thread.start()

        self.plotTimer = QTimer()
        self.plotTimer.timeout.connect(self.simulate)
        self.plotTimer.start(5)

    def serial_read(self):
        while True:
            received_data = serial_read(self.ser)
            if received_data is not None and isinstance(received_data, dict):
                self.update_frames(received_data)

    def update_frames(self, new_data):
        for frame in self.frames:
            if frame['id'] == new_data['id']:
                frame['data'] = new_data['data']
                return
        # If the ID does not exist, add the new data
        self.frames.append(new_data)

    def simulate(self):
        self.table.populate_table(self.frames, self.found_action_frames)

    def get_current_frames(self):
        return self.frames

    def set_current_frames(self, id, idx, val):
        for index, frame in enumerate(self.frames):
            if id == frame['id']:
                idx = idx * 2
                new_data = frame['data'][:idx] + format(val, '02') + frame['data'][idx + 2:]
                self.initial_frames[index]['data'] = new_data

    def enable_recording_buttons(self):
        self.recordButton.hide()
        self.captureIdleButton.show()
        self.captureThrottleButton.show()
        self.captureBrakeButton.show()
        self.captureSteerRightButton.show()
        self.captureSteerLeftButton.show()

    def enable_capture(self, button_name):
        print(f"Capture triggered by: {button_name}")

        # Disable the pressed button
        if button_name in self.capture_button_enable:
            self.capture_button_enable[button_name](False)

        # Hide all buttons if all were clicked
        if all(not button.isEnabled() for button in
               [self.captureIdleButton, self.captureThrottleButton,
                self.captureBrakeButton,
                self.captureSteerLeftButton,
                self.captureSteerRightButton]):
            self.captureIdleButton.hide()
            self.captureThrottleButton.hide()
            self.captureBrakeButton.hide()
            self.captureSteerRightButton.hide()
            self.captureSteerLeftButton.hide()

            self.findFramesButton.clicked.connect(self.find_action_frames)
            self.trainButton.clicked.connect(self.train_model)
            self.findFramesButton.show()
            self.trainButton.show()

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
            print(
                f"The {label} frame ID is {best_frame_id} and byte position {best_byte} has the most linear relationship with an R-squared of {best_r_squared:.2f}")

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

        self.starPredictButton.show()
        self.stopPredictButton.show()
        self.starPredictButton.clicked.connect(self.start_predict)
        self.stopPredictButton.clicked.connect(self.stop_predict)
        self.trainButton.hide()
        self.sim_control.state_label.show()

    def start_predict(self):
        # Capture for period of duration
        self.run_predict = True
        predict_thread = threading.Thread(target=self.predict)
        predict_thread.start()

    def stop_predict(self):
        self.run_predict = False
        self.sim_control.state_label.hide()

    def predict(self):
        self.sim_control.state_label.show()
        while self.run_predict:
            frames = self.capture(1)
            self.sim_control.state_label.setText(self.predictor.predict(frames,
                                                                        self.frame_count))
            time.sleep(0.001)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
