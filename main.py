import sys
import src
import random
import primaryWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QInputDialog
from PySide6.QtCore import Slot, QTimer


class PrimaryWindowClass(QMainWindow, primaryWindow.Ui_primaryWindow):
    data = 0
    variable_frames = []
    static_frames = []
    variable_bytes_idx = []
    throttle_bytes = []
    brake_bytes = []
    steering_bytes = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resize(950, 1000)
        self.startButton.clicked.connect(self.generate_data)

    def add_row(self, row_data):
        row_position = self.mainTable.rowCount()
        self.mainTable.insertRow(row_position)
        for column, data in enumerate(row_data):
            item = QTableWidgetItem(str(data))
            self.mainTable.setItem(row_position, column, item)

    def clear_table(self):
        self.mainTable.clearContents()
        self.mainTable.setRowCount(0)

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

    # def simulateVariableBytes(self):
    #     for frame in self.variableFrames:

    @Slot()
    def generate_data(self):
        print('\nGenerate start\n')
        frame_count = self.open_input_dialog()
        self.data = src.generateFrames(
            frame_count)  # REMOVE THE ADDED "0x" IN generateFrames AND FIX THE CODE AS SUCH!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        if frame_count != 0:  # If the user hits cancel when prompted to enter number of needed frames
            data_row = []
            # Format the data such that it can fit into 9 columns (ID , 0-7) where each column has 1 byte
            for frame in self.data:
                data_row.append(frame.id)
                for i in range(2, len(frame.data), 2):
                    data_row.append("0x" + frame.data[i:i + 2])
                data_row_copy = data_row.copy()
                self.add_row(data_row_copy)
                data_row.clear()
            self.startButton.hide()  # Grey out the start button
            print('\nGenerate finish\n')

            self.start_simulation()

    @Slot()
    def start_simulation(self):
        print("Simulation start")
        # Split data in variable and static frames with a ratio of 0.6 to 0.4
        self.variable_frames, self.static_frames = src.splitFrames(self.data)
        print(self.variable_frames[0].data)
        # Generate indexes at random for variable bytes
        self.variable_bytes_idx, self.throttle_bytes, self.brake_bytes, self.steering_bytes = src.generateVariableBytesIdx(
            self.variable_frames)

        # Running
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.simulateVariableBytes)
        # self.timer.start(1000)  # Call every 1000 milliseconds (1 second)

        print("Simulation finish")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PrimaryWindowClass()

    window.show()
    sys.exit(app.exec())
