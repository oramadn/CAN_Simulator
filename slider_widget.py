from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider
from PySide6.QtCore import Qt

class SliderControl(QWidget):
    def __init__(self, max_value=255):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(max_value)
        self.layout.addWidget(self.slider)

    def valueChanged(self, slot):
        self.slider.valueChanged.connect(slot)  # External connection to handle value changes
