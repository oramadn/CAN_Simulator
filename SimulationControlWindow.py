from throttle_widget import GaugeWidget
from brake_widget import DashedBarWidget
from steering_widget import SteeringWheelWidget
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QApplication, QPushButton, \
    QSpacerItem, QSizePolicy


class SimulationControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Throttle and Brake Controls")
        self.setup_ui()

    def reset_throttle_slider(self):
        """Slot to reset the throttle slider to its default position."""
        self.throttle_slider.setValue(0)

    def reset_brake_slider(self):
        """Slot to reset the brake slider to its default position."""
        self.brake_slider.setValue(0)

    def reset_steering_slider(self):
        """Slot to reset the steering slider to its default position."""
        self.steering_slider.setValue(127)

    def setup_ui(self):
        # Overall layout container
        main_layout = QVBoxLayout()  # This will hold everything

        button_layout = QHBoxLayout()
        title_layout = QHBoxLayout()
        gadget_layout = QHBoxLayout()

        # Capturing buttons
        self.captureIdleButton = QPushButton("Record Idle")
        self.captureThrottleButton = QPushButton("Record Throttle")
        self.captureBrakeButton = QPushButton("Record Brake")
        self.captureSteerRightButton = QPushButton("Record Steer Right")
        self.captureSteerLeftButton = QPushButton("Record Steer Left")
        button_layout.addWidget(self.captureIdleButton)
        button_layout.addWidget(self.captureThrottleButton)
        button_layout.addWidget(self.captureBrakeButton)
        button_layout.addWidget(self.captureSteerRightButton)
        button_layout.addWidget(self.captureSteerLeftButton)

        # Throttle title
        self.throttle_label = QLabel("Throttle")
        self.throttle_label.setAlignment(Qt.AlignCenter)
        self.throttle_label.setFont(QFont('Arial', 20, QFont.Bold))
        self.throttle_label.setStyleSheet("QLabel { color : #ffffff; }")

        title_layout.addWidget(self.throttle_label)

        # Throttle layout
        throttle_layout = QVBoxLayout()

        self.throttle_gauge = GaugeWidget()
        self.throttle_slider = QSlider(Qt.Horizontal)
        self.throttle_slider.setMinimum(0)
        self.throttle_slider.setMaximum(255)
        self.throttle_slider.valueChanged.connect(self.throttle_gauge.set_value)

        # Add reset button
        self.reset_throttle_button = QPushButton("Reset throttle")
        self.reset_throttle_button.clicked.connect(self.reset_throttle_slider)

        throttle_layout.addWidget(self.throttle_gauge)
        throttle_layout.addWidget(self.throttle_slider)
        throttle_layout.addWidget(self.reset_throttle_button)

        # Brake title
        self.brake_label = QLabel("Brakes")
        self.brake_label.setAlignment(Qt.AlignCenter)
        self.brake_label.setFont(QFont('Arial', 20, QFont.Bold))
        self.brake_label.setStyleSheet("QLabel { color : #ffffff; }")

        title_layout.addWidget(self.brake_label)

        # Brake layout
        brake_layout = QVBoxLayout()

        upper_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.brake_gauge = DashedBarWidget()
        lower_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.brake_slider = QSlider(Qt.Horizontal)
        self.brake_slider.setMinimum(0)
        self.brake_slider.setMaximum(255)
        self.brake_slider.valueChanged.connect(self.brake_gauge.set_value)

        # Add reset button
        self.reset_brake_button = QPushButton("Reset brake")
        self.reset_brake_button.clicked.connect(self.reset_brake_slider)

        brake_layout.addItem(upper_spacer)
        brake_layout.addWidget(self.brake_gauge)
        brake_layout.addItem(lower_spacer)
        brake_layout.addWidget(self.brake_slider)
        brake_layout.addWidget(self.reset_brake_button)

        # Steering title
        self.steering_label = QLabel("Steering wheel")
        self.steering_label.setAlignment(Qt.AlignCenter)
        self.steering_label.setFont(QFont('Arial', 20, QFont.Bold))
        self.steering_label.setStyleSheet("QLabel { color : #ffffff; }")

        title_layout.addWidget(self.steering_label)

        # Steering Layout
        steering_layout = QVBoxLayout()

        self.steering_gauge = SteeringWheelWidget()
        self.steering_slider = QSlider(Qt.Horizontal)
        self.steering_slider.setMinimum(0)
        self.steering_slider.setMaximum(255)
        self.steering_slider.setValue(127)  # Initialize at the midpoint
        self.steering_slider.valueChanged.connect(self.steering_gauge.set_value)

        # Add reset button
        self.reset_steering_button = QPushButton("Reset Steering")
        self.reset_steering_button.clicked.connect(self.reset_steering_slider)

        steering_layout.addWidget(self.steering_gauge)
        steering_layout.addWidget(self.steering_slider)
        steering_layout.addWidget(self.reset_steering_button)

        # Add throttle and brake layouts to main layout
        gadget_layout.addLayout(throttle_layout)
        gadget_layout.addLayout(brake_layout)
        gadget_layout.addLayout(steering_layout)

        # Driving state label
        self.state_label = QLabel("State")
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.state_label.setStyleSheet("QLabel { color : #cccccc; }")

        # Add layouts to the main window layout
        main_layout.addLayout(button_layout)
        main_layout.addLayout(title_layout)
        main_layout.addLayout(gadget_layout)
        main_layout.addWidget(self.state_label)

        # Set the main layout to the widget
        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    control_window = SimulationControl()
    control_window.show()
    sys.exit(app.exec())
