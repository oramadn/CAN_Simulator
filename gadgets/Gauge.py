import sys
import math
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtWidgets import QWidget, QApplication, QLabel


class GaugeWidget(QWidget):
    def __init__(self, min_val=0, max_val=180):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.setFixedSize(250, 250)  # Set a fixed size for the widget
        self.value = 0
        self.radius = 110  # Set this to half of your widget size minus the stroke width
        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparency
        self.setWindowFlags(Qt.FramelessWindowHint)  # Removes the window frame if it's a standalone window

    def update_radius(self):
        self.radius = min(self.width(), self.height()) // 2 - 10  # Adjust the padding if needed

    def set_value(self, val):
        self.value = val
        self.repaint()

    def resizeEvent(self, event):
        self.update_radius()  # Update the radius when widget is resized
        self.repaint()  # Ensure repaint to adjust drawing to new size

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2)
        painter.setPen(QPen(QColor(0, 119, 190), 2))  # Adjust pen size for smaller widget
        painter.setBrush(QBrush(QColor(0, 0, 0)))  # Black brush for gauge
        painter.drawEllipse(center, self.radius, self.radius)

        self.draw_numbers(painter, center)

        # Update needle calculation for smaller size
        start_angle = 210
        end_angle = 510
        angle_range = end_angle - start_angle
        angle = start_angle + angle_range * (self.value / 255)
        rad_angle = math.radians(angle)
        needle_len = self.radius * 0.9
        needle_end = QPoint(center.x() + needle_len * math.sin(rad_angle),
                            center.y() - needle_len * math.cos(rad_angle))
        painter.setPen(QPen(Qt.red, 2))  # Adjust pen size for smaller widget
        painter.drawLine(center, needle_end)

    def draw_numbers(self, painter, center):
        painter.setFont(QFont('Arial', 10))
        painter.setPen(QColor(255, 255, 255))  # Set pen for numbers
        start_angle = 210
        end_angle = 510
        number_of_steps = 10  # Define the number of major steps around the gauge
        angle_increment = (end_angle - start_angle) / (number_of_steps - 1)
        tick_length = 10  # Length of major ticks
        small_tick_length = 5  # Length of minor ticks
        value_increment = (self.max_val - self.min_val) / (number_of_steps - 1)

        # Draw major ticks and numbers
        for i in range(number_of_steps):
            angle = start_angle + i * angle_increment
            rad_angle = math.radians(angle)
            value = self.min_val + i * value_increment  # Calculate the value to display
            # Draw major tick
            self.draw_tick(painter, center, rad_angle, self.radius, tick_length, QColor(255, 255, 255), Qt.SolidLine)
            # Draw number
            text_x = center.x() + (self.radius - 22) * math.sin(rad_angle) - 10
            text_y = center.y() - (self.radius - 22) * math.cos(rad_angle) + 5
            painter.drawText(text_x, text_y, f"{int(value)}")  # Display integer value

        # Draw minor ticks
        minor_angle_increment = angle_increment / 5  # Five minor ticks per major tick interval
        for i in range((number_of_steps - 1) * 5):
            angle = start_angle + (i + 1) * minor_angle_increment
            rad_angle = math.radians(angle)
            # Draw minor tick
            if (i + 1) % 5 != 0:  # Avoid drawing minor tick on top of major tick
                self.draw_tick(painter,
                               center,
                               rad_angle,
                               self.radius,
                               small_tick_length,
                               QColor(255, 255, 255),
                               Qt.DashLine)

    def draw_tick(self, painter, center, rad_angle, radius, length, color, pen_style):
        painter.setPen(QPen(color, 2, pen_style))
        outer_point = QPoint(center.x() + radius * math.sin(rad_angle),
                             center.y() - radius * math.cos(rad_angle))
        inner_point = QPoint(center.x() + (radius - length) * math.sin(rad_angle),
                             center.y() - (radius - length) * math.cos(rad_angle))
        painter.drawLine(outer_point, inner_point)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GaugeWidget()
    window.show()
    sys.exit(app.exec())
