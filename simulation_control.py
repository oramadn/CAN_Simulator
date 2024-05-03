from throttle_widget import GaugeWidget
from brake_widget import DashedBarWidget
from steering_widget import SteeringWheelWidget
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel


class SimulationControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Throttle and Brake Controls")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # Create label,gauge and slider for throttle
        throttle_layout = QVBoxLayout()

        self.throttle_label = QLabel("Throttle")
        self.throttle_label.setAlignment(Qt.AlignCenter)
        self.throttle_label.setFont(QFont('Arial', 20, QFont.Bold))
        self.throttle_label.setStyleSheet("QLabel { color : #ffffff; }")

        self.throttle_gauge = GaugeWidget()
        self.throttle_slider = QSlider(Qt.Horizontal)
        self.throttle_slider.setMinimum(0)
        self.throttle_slider.setMaximum(255)
        self.throttle_slider.valueChanged.connect(self.throttle_gauge.set_value)

        throttle_layout.addWidget(self.throttle_label)
        throttle_layout.addWidget(self.throttle_gauge)
        throttle_layout.addWidget(self.throttle_slider)

        # Create gauge and slider for brake
        brake_layout = QVBoxLayout()

        self.brake_label = QLabel("Brakes")
        self.brake_label.setAlignment(Qt.AlignCenter)
        self.brake_label.setFont(QFont('Arial', 20, QFont.Bold))
        self.brake_label.setStyleSheet("QLabel { color : #ffffff; }")

        self.brake_gauge = DashedBarWidget()
        self.brake_slider = QSlider(Qt.Horizontal)
        self.brake_slider.setMinimum(0)
        self.brake_slider.setMaximum(255)
        self.brake_slider.valueChanged.connect(self.brake_gauge.set_value)

        brake_layout.addWidget(self.brake_label)
        brake_layout.addWidget(self.brake_gauge)
        brake_layout.addWidget(self.brake_slider)

        # Create gauge and slider for steering
        steering_layout = QVBoxLayout()

        self.steering_label = QLabel("Steering wheel")
        self.steering_label.setAlignment(Qt.AlignCenter)
        self.steering_label.setFont(QFont('Arial', 20, QFont.Bold))
        self.steering_label.setStyleSheet("QLabel { color : #ffffff; }")

        self.steering_gauge = SteeringWheelWidget()
        self.steering_slider = QSlider(Qt.Horizontal)
        self.steering_slider.setMinimum(0)
        self.steering_slider.setMaximum(255)
        self.steering_slider.setValue(127)  # Initialize at the midpoint
        self.steering_slider.valueChanged.connect(self.steering_gauge.set_value)

        steering_layout.addWidget(self.steering_label)
        steering_layout.addWidget(self.steering_gauge)
        steering_layout.addWidget(self.steering_slider)

        # Add throttle and brake layouts to main layout
        main_layout.addLayout(throttle_layout)
        main_layout.addLayout(brake_layout)
        main_layout.addLayout(steering_layout)

        # Set the main layout to the widget
        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    control_window = SimulationControl()
    control_window.show()
    sys.exit(app.exec())
