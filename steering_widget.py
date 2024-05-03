from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider
from PySide6.QtGui import QPainter, QPixmap, QTransform
from PySide6.QtCore import Qt


class SteeringWheelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.steering_wheel_image = QPixmap("steering_wheel.png")
        if self.steering_wheel_image.isNull():
            print("Failed to load the steering wheel image.")
        else:
            self.setFixedSize(self.steering_wheel_image.size())

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

