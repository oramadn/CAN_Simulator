import sys
import test_ui
from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow
from PySide6.QtCore import Slot


class GUI(QMainWindow,test_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.sayHello)

    @Slot()
    def sayHello(self):
        print('Hello!1!!!')

def main():
    app = QApplication(sys.argv)
    gui = GUI()

    gui.show()
    app.exec_()

if __name__ == '__main__':
    main()
