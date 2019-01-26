#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication
import sys

from main_window import MainWindow
from helper import BorgException, show_error

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    try:
        window.config.read()
    except BorgException as e:
        show_error(e)
        sys.exit(1)

    sys.exit(app.exec_())
