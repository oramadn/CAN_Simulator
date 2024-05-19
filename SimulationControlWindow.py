import sys
import math

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap, QTransform
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QApplication, QPushButton, \
    QSpacerItem, QSizePolicy

from gadgets.GaugeGadget import GaugeWidget


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

        # Throttle title
        self.throttle_label = QLabel("Throttle")
        self.throttle_label.setAlignment(Qt.AlignCenter)
        self.throttle_label.setFont(QFont('Arial', 20, QFont.Bold))
        self.throttle_label.setStyleSheet("QLabel { color : #ffffff; }")

        title_layout.addWidget(self.throttle_label)

        # Throttle layout
        throttle_layout = QVBoxLayout()

        self.throttle_gauge = GaugeWidget()
        self.throttle_gauge.setFixedSize(300, 300)
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
        self.brake_gauge = BrakeWidget()
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


class BrakeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 30)  # Set minimum size of the widget
        self.value = 0

    def set_value(self, value):
        self.value = value
        self.update()  # Redraw the widget when the value changes

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        num_dashes = 10
        dash_width = (self.width() - 20) / num_dashes - 2
        dash_height = 20

        painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        painter.drawRect(10, 5, self.width() - 20, 20)

        dashes_to_fill = int((self.value / 255) * num_dashes)
        for i in range(dashes_to_fill):
            if self.value < 85:
                color = QColor(0, 255, 0)  # Green
            elif 85 <= self.value < 170:
                color = QColor(255, 255, 0)  # Yellow
            else:
                color = QColor(255, 0, 0)  # Red

            x = 12 + i * (dash_width + 2)
            painter.fillRect(x, 7, dash_width, dash_height, color)


class SteeringWheelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.steering_wheel_image = QPixmap("images/steering_wheel.png")
        if self.steering_wheel_image.isNull():
            print("Failed to load the steering wheel image.")
        else:
            self.setMinimumSize(self.steering_wheel_image.size())

        self.angle = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rotated_pixmap = self.steering_wheel_image.transformed(
            QTransform().rotate(self.angle), Qt.SmoothTransformation)
        x = (self.width() - rotated_pixmap.width()) / 2
        y = (self.height() - rotated_pixmap.height()) / 2
        painter.drawPixmap(x, y, rotated_pixmap)

    def set_value(self, value):
        # Adjust the angle computation to ensure accurate mapping.
        self.angle = ((value - 127.5) / 127.5) * 360
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    control_window = SimulationControl()
    control_window.show()
    sys.exit(app.exec())
