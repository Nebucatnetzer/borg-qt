import os

from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMainWindow

from settings import Settings
from config import Config


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Borg Interface")
        QCoreApplication.setApplicationName("borg-qt")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/MainWindow.ui')
        uic.loadUi(ui_path, self)

        self.config = Config()

        self.action_settings.triggered.connect(self.show_settings)

    def show_settings(self):
        self.config.set_form_values()
        self.config.exec_()
