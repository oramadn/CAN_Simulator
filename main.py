# import sys
# import test_ui
# from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow
# from PySide6.QtCore import Slot


# class GUI(QMainWindow,test_ui.Ui_MainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)
#         self.pushButton.clicked.connect(self.sayHello)

#     @Slot()
#     def sayHello(self):
#         print('Hello!1!!!')

# def main():
#     app = QApplication(sys.argv)
#     gui = GUI()

#     gui.show()
#     app.exec_()

# if __name__ == '__main__':
#     main()

import time
import random

class CANmsg:
    def __init__(self, id=None, data=None):
        self.id = id
        self.data = data

def generateFrames(frameCount):
    #Generate random IDs and DATA
    frames = []
    for i in range(frameCount):
        random_id = '0x' + hex(random.randint(0, 2**11 - 1))[2:].rjust(5, '0')
        random_data = '0x' + hex(random.randint(0, 2**64 - 1))[2:].rjust(16, '0')

        frames.append(CANmsg(random_id,random_data))
        
    frames = sorted(frames, key=lambda x: x.id)

    #Prepare data for making a table
    data = []
    data_row = []
    for frame in frames:
        data_row.append(frame.id)
        for i in range(2, len(frame.data), 2):
            data_row.append("0x" + frame.data[i:i+2])
        data_row_copy = data_row.copy()
        data.append(data_row_copy)
        data_row.clear()

    return data

def generateTable(data):
    data.insert(0,("ID","0","1","2","3","4","5","6","7"))
    # Determine the maximum width for each column
    column_widths = [max(len(str(item)) for item in column) for column in zip(*data)]

    # Centered column titles
    for i, column_title in enumerate(data[0]):
        print(f"{column_title.center(column_widths[i])}", end="  ")
    print()

    # Print the table
    for row in data[1:]:
        for i, item in enumerate(row):
            print(f"{item:{'>' if isinstance(item, int) else '<'}{column_widths[i]}}", end="  ")
        print()

def main():
    while(True):
        try:
            frameCount = int(input("How many CAN frames would you like to simulate (10-100): "))
        except ValueError:
            print("\nInvalid input")
            continue   
        if frameCount < 10 or frameCount > 100:
            print("\nInvalid amount of CAN messages requested")
            continue
        break

    data = generateFrames(frameCount)
    #generateTable(data)
    

if __name__ == '__main__':
    main()