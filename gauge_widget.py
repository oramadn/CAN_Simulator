from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QFont
from PySide6.QtWidgets import QVBoxLayout, QSlider, QWidget, QApplication

class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.painter = 0  # Initialize progress as 0
        self.setMinimumSize(50, 50)  # Set minimum size of the widget

    def update_progress(self, pp):
        """Update the progress value and repaint if it changes."""
        if self.painter == pp:
            return
        self.painter = pp
        self.update()

    def paintEvent(self, event):
        """Custom paint event to draw the circular progress bar."""
        # Ensure widget remains square (aspect ratio 1:1)
        if self.height() > self.width():
            self.setFixedWidth(self.height())
        if self.width() > self.height():
            self.setFixedHeight(self.width())

        # Degrees of progress and remaining progress
        progress_degree = self.painter * 360
        remaining_degree = 360 - progress_degree

        painter = QPainter(self)
        painter.translate(4, 4)  # Offset painter for aesthetics
        painter.setRenderHint(QPainter.Antialiasing)  # Enable anti-aliasing

        # Setup the paths for progress and remaining progress
        path, path2 = QPainterPath(), QPainterPath()
        circle_width = self.width() - self.width() / 10
        width_half = circle_width / 2
        path.moveTo(width_half, 0)
        circle_rect = QRectF(self.rect().left() / 2, self.rect().top() / 2,
                             circle_width, self.height() - self.height() / 10)
        path.arcTo(circle_rect, 90, -progress_degree)

        # Configure pen for drawing the progress
        pen = QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(QColor("#30b7e0"))
        pen.setWidth(self.width() / 25)
        painter.strokePath(path, pen)

        # Setup the path for the remaining progress circle
        path2.moveTo(width_half, 0)
        pen2 = QPen()
        pen2.setWidth(self.width() / 25)
        pen2.setColor(QColor("#d7d7d7"))
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([0.5, 1.105])  # Dashed pattern for remaining progress
        path2.arcTo(circle_rect, 90, remaining_degree)
        pen2.setDashOffset(2.2)
        painter.strokePath(path2, pen2)

        # Draw the text percentage in the middle
        painter.setPen(pen)
        font = QFont()
        percent_size = self.height() / 7
        font.setPointSizeF(percent_size)
        painter.setFont(font)
        percent_text_position = self.rect().center()
        percent_in_text = self.painter * 100
        # Adjust text position based on the size of the number
        percent_text_position.setX(percent_text_position.x() - (
            percent_size + (self.width() / 6 if percent_in_text >= 100
            else self.width() / 10 if percent_in_text >= 10 else self.width() / 40)))
        percent_text_position.setY(percent_text_position.y() + percent_size * 2 / 5)
        painter.drawText(percent_text_position, f"{round(self.painter * 100, 0)}%")

class GaugeWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        progress_bar = CircularProgressBar(self)
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(0)
        slider.setMaximum(100)
        layout.addWidget(progress_bar)
        layout.addWidget(slider)
        self.setLayout(layout)
        # Connect slider value change to progress bar update
        slider.valueChanged.connect(lambda value: progress_bar.update_progress(value / slider.maximum()))

if __name__ == '__main__':
    app = QApplication()
    main_widget = GaugeWidget()
    main_widget.show()
    app.exec()
