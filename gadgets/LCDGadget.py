import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLCDNumber
from PySide6.QtCore import Qt
import random


class LCDWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.lcd = QLCDNumber(self)
        self.lcd.setFixedSize(160, 100)
        self.lcd.setDigitCount(3)  # Display up to 3 digits
        self.lcd.display(0)  # Start with 0

        # Set the style of the LCD
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.setStyleSheet("""
                    QLCDNumber {
                        background-color: transparent;
                        color: rgb(0, 119, 190);
                    }
                """)

        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparency
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout()
        layout.addWidget(self.lcd)
        self.setLayout(layout)

    def set_value(self, val):
        self.value = val
        self.lcd.display(val)  # Display the value on the LCD


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LCDWidget()
    ex.show()
    sys.exit(app.exec())
