from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QPoint, QSize
import math

# class MyDevice:
#     def __init__(self):
#         self.value = 0x00
#
#     def set_value(self, val):
#         self.value = val
#         print(f"Device value set to {self.value:02X}")

class GaugeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 300)
        self.value = 0
        self.radius = self.calculate_radius()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 16, QFont.Bold))
        self.label.setStyleSheet("QLabel { color : #0077be; }")
        self.update_label_position()

    def set_value(self, val):
        self.value = val
        km_value = int(val / 255 * 180)
        self.label.setText(f"{km_value} km")
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.radius = self.calculate_radius()

        painter.setBrush(QBrush(QColor(0, 0, 0)))  # Black background
        painter.drawRect(0, 0, self.width(), self.height())

        center = QPoint(self.width() // 2, self.height() // 2)
        painter.setPen(QPen(QColor(0, 119, 190), 4))
        painter.setBrush(QBrush(QColor(146, 141, 150)))
        painter.drawEllipse(center, self.radius, self.radius)

        self.draw_numbers(painter, center)

        start_angle = 210
        end_angle = 510
        angle_range = end_angle - start_angle
        angle = angle_range * (self.value / 255) + start_angle
        rad_angle = math.radians(angle)
        needle_len = self.radius * 0.9
        needle_end = QPoint(center.x() + needle_len * math.sin(rad_angle),
                            center.y() - needle_len * math.cos(rad_angle))
        painter.setPen(QPen(Qt.red, 4))
        painter.drawLine(center, needle_end)

        self.update_label_position()

    def calculate_radius(self):
        return min(self.width(), self.height()) // 3 - 20

    def update_label_position(self):
        label_width = 100
        label_height = 30
        self.label.resize(label_width, label_height)
        self.label.move(self.width() // 2 - label_width // 2,
                        self.height() // 2 - self.radius - label_height - 30)

    def draw_numbers(self, painter, center):
        painter.setFont(QFont('Arial', 10))
        painter.setPen(QColor(0, 119, 190))
        start_angle = 210
        end_angle = 510
        increments = 20
        number_of_steps = 180 // increments + 1
        angle_increment = (end_angle - start_angle) / (number_of_steps - 1)

        for i in range(number_of_steps):
            angle = start_angle + i * angle_increment
            rad_angle = math.radians(angle)
            text_x = center.x() + (self.radius + 20) * math.sin(rad_angle) - 10
            text_y = center.y() - (self.radius + 20) * math.cos(rad_angle) + 5
            painter.drawText(text_x, text_y, f"{i * increments}")
