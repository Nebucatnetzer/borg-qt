import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMainWindow

from config import Config
from helper import BorgException, show_error


class MainWindow(QMainWindow):
    """The main window of the application. It provides the various functions to
    control BorgBackup."""
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        QCoreApplication.setApplicationName("borg-qt")

        # Load the UI file to get the dialogs layout.
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/MainWindow.ui')
        uic.loadUi(ui_path, self)

        # Set the window title after the UI has been loaded. Otherwise it gets
        # overwritten.
        self.setWindowTitle("Borg-Qt")

        # Create a Config object for storing the configuration.
        self.config = Config()

        # Connecting actions and buttons.
        self.action_settings.triggered.connect(self.show_settings)

    def start(self):
        """This method is intendet to be used only once at the application
        start. It reads the configuration file and sets the required
        environment variables."""
        try:
            self.config.read()
            self.config._set_environment_variables()
        except BorgException as e:
            show_error(e)
            sys.exit(1)

    def show_settings(self):
        """Display the settings dialog."""
        self.config.set_form_values()
        self.config.exec_()
