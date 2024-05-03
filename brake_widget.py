from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt

class DashedBarWidget(QWidget):
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
