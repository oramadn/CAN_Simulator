import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt

class VerticalBarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Initialize the progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setFixedHeight(130)
        self.progressBar.setOrientation(Qt.Vertical)  # Set the progress bar to vertical
        self.progressBar.setMaximum(255)  # Ensure the maximum is set to 255
        self.progressBar.setValue(0)  # Start at 0 to show the effect clearly

        # Set custom styling
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: #f3f3f3;
            }
            QProgressBar::chunk {
                background-color: rgb(0, 119, 190);
            }
        """)

        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparency
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.progressBar.setTextVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.progressBar)

    def set_value(self, val):
        self.value = val
        self.progressBar.setValue(self.value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VerticalBarWidget()
    window.show()
    sys.exit(app.exec())
