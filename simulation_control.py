from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider
from throttle_widget import GaugeWidget
from brake_widget import DashedBarWidget
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow

class ThrottleBrakeControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Throttle and Brake Controls")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Create gauge and slider for throttle
        self.throttle_gauge = GaugeWidget()
        self.throttle_slider = QSlider(Qt.Horizontal)
        self.throttle_slider.setMinimum(0)
        self.throttle_slider.setMaximum(255)
        self.throttle_slider.valueChanged.connect(self.throttle_gauge.set_value)

        # Create gauge and slider for brake
        self.brake_gauge = DashedBarWidget()
        self.brake_slider = QSlider(Qt.Horizontal)
        self.brake_slider.setMinimum(0)
        self.brake_slider.setMaximum(255)
        self.brake_slider.valueChanged.connect(self.brake_gauge.set_value)

        # Add widgets to the layout
        layout.addWidget(self.throttle_gauge)
        layout.addWidget(self.throttle_slider)
        layout.addWidget(self.brake_gauge)
        layout.addWidget(self.brake_slider)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    control_window = ThrottleBrakeControl()
    control_window.show()
    sys.exit(app.exec())
