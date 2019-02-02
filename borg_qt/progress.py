import os
import time

from PyQt5.QtWidgets import QDialog
from PyQt5 import uic


class ProgressDialog(QDialog):
    """The main window of the application. It provides the various functions to
    control BorgBackup."""
    def __init__(self, thread):
        super(ProgressDialog, self).__init__()
        # Load the UI file to get the dialogs layout.
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/Progress.ui')
        uic.loadUi(ui_path, self)
        self.thread = thread
        self.thread.finished.connect(self.close)
        self.thread.start()

    def reject(self):
        self.thread.stop()
        super().reject()
