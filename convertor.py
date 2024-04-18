import subprocess

subprocess.check_output(['pyside6-uic', 'test.ui', '-o', 'test_ui.py'])