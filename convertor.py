import subprocess

subprocess.check_output(['pyside6-uic', 'xml/primaryWindow.ui', '-o', 'primaryWindow.py'])
subprocess.check_output(['pyside6-uic', 'xml/inputWindow.ui', '-o', 'inputWindow.py'])