#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication
import sys

from main_window import MainWindow

if __name__ == "__main__":
    # creates the main application, only one of these is every needed
    # in an application
    app = QApplication(sys.argv)
    # creates a new window, you can have multiple of these
    window = MainWindow()
    # show the window, they are hidden by default
    window.show()
    window.config.read()

    # start the application
    sys.exit(app.exec_())
