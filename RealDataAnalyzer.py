import sys
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
                               QTableWidgetItem, QLabel, QInputDialog)
from PySide6.QtCore import QTimer

from frame_generator import generate_random_frames
from SimulationControlWindow import SimulationControl

RANDOM_SEED = None


class DataTable(QTableWidget):
    def __init__(self):
        super().__init__(0, 9)  # Initialize with 0 rows and 9 columns
        self.setHorizontalHeaderLabels(['ID', '0', '1', '2', '3', '4', '5', '6', '7'])
        self.setColumnWidth(0, 100)  # Wider column for ID
        for i in range(1, 9):
            self.setColumnWidth(i, 30)  # Set the width for byte columns

    def populate_table(self, frames):
        self.setRowCount(len(frames))
        for row, frame in enumerate(frames):
            self.setItem(row, 0, QTableWidgetItem(frame['id']))
            data = frame['data']
            # Select a random data frame if there are multiple
            if isinstance(data, list):
                data = random.choice(data)
            # Fill in the bytes
            for col in range(1, 9):
                try:
                    byte = data[(col - 1) * 2:(col - 1) * 2 + 2]  # Each byte takes two hex characters
                    self.setItem(row, col, QTableWidgetItem(byte))
                except IndexError:
                    self.setItem(row, col, QTableWidgetItem(''))


class DataGadgets(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Gadgets Based on Data")
        layout.addWidget(label)
        self.setLayout(layout)


class DataControls(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        sim_control = SimulationControl()
        layout.addWidget(sim_control)
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
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        selected_option = self.open_combo_box()
        if selected_option == "Real data":
            self.init_real_window()
        else:
            self.init_simulation_window()

    def open_combo_box(self):
        options = ["Real data", "Simulated data"]
        selected_option, ok = QInputDialog.getItem(self, "Select Option", "Choose an option:", options, 0, False)
        if ok and selected_option:
            print(f"Selected Option: {selected_option}")
            return selected_option

    def init_real_window(self):
        top_buttons_layout = QHBoxLayout()
        button1 = QPushButton("Top Button 1")
        button2 = QPushButton("Top Button 2")
        top_buttons_layout.addWidget(button1)
        top_buttons_layout.addWidget(button2)

        content_layout = QHBoxLayout()
        self.controls = DataControls()
        self.table = DataTable()
        content_layout.addWidget(self.controls)
        content_layout.addWidget(self.table)

        right_layout = QVBoxLayout()
        gadgets = DataGadgets()
        plotter = DataPlotter()

        right_layout.addWidget(gadgets)
        right_layout.addWidget(plotter)

        content_layout.addLayout(right_layout)

        self.main_layout.addLayout(top_buttons_layout)
        self.main_layout.addLayout(content_layout)

    def init_simulation_window(self):
        top_layout = QHBoxLayout()
        # button1 = QPushButton("Top Button 1")
        # button2 = QPushButton("Top Button 2")
        # top_layout.addWidget(button1)
        # top_layout.addWidget(button2)

        content_layout = QHBoxLayout()
        table_layout = QVBoxLayout()
        self.table = DataTable()
        self.controls = DataControls()
        table_layout.addWidget(self.table)
        table_layout.addWidget(self.controls)
        content_layout.addLayout(table_layout)

        right_layout = QVBoxLayout()
        gadgets = DataGadgets()
        plotter = DataPlotter()

        right_layout.addWidget(gadgets)
        right_layout.addWidget(plotter)

        content_layout.addLayout(right_layout)



        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(content_layout)


        self.frame_count = self.open_input_dialog()

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

    def setup_simulation(self):
        self.frames = generate_random_frames(self.frame_count)
        self.throttleFrame, self.brakeFrame, self.steeringFrame = self.frames[0], self.frames[1], self.frames[2]

        self.assign_random_byte_for_action(self.throttleFrame)
        self.assign_random_byte_for_action(self.brakeFrame)
        self.assign_random_byte_for_action(self.steeringFrame, 2)
        random.shuffle(self.frames)

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate)
        self.timer.start(50)

    def assign_random_byte_for_action(self, frame, num_bytes=1):
        random.seed(RANDOM_SEED)
        even_indices = list(range(0, len(frame['data']), 2))
        selected_indices = random.sample(even_indices, num_bytes)
        selected_bytes = [frame['data'][idx:idx + 2] for idx in selected_indices]
        frame['byte'] = selected_bytes
        frame['byte idx'] = selected_indices

    def simulate(self):
        self.table.populate_table(self.frames)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
