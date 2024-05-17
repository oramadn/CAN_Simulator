import runpy
import gc

from PySide6.QtWidgets import QApplication, QInputDialog

import SimulatedDataAnalyzer

while True:
    selected_option = int(input("Pick the desired version:\n[1]. Real data\n[2]. Simulated data\n\n"))
    if selected_option != 1 and selected_option != 2:
        print("Please choose a valid option!")
    break


if selected_option == 1:
    pass
else:
    SimulatedDataAnalyzer.main()
