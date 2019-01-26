#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication
import sys

from main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.start()

    sys.exit(app.exec_())
