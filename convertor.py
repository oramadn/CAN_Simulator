import subprocess

subprocess.check_output(['pyside6-uic', 'xml/primaryWindow.ui', '-o', 'primaryWindow.py'])