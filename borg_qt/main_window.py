import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMainWindow

from config import Config
from helper import BorgException, show_error


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        QCoreApplication.setApplicationName("borg-qt")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/MainWindow.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Borg-Qt")

        self.config = Config()

        self.action_settings.triggered.connect(self.show_settings)

    def start(self):
        try:
            self.config.read()
            self.config._set_environment_variables()

        except BorgException as e:
            show_error(e)
            sys.exit(1)

    def show_settings(self):
        self.config.set_form_values()
        self.config.exec_()
