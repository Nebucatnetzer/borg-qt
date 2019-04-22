import os

from PyQt5.QtWidgets import QDialog
from PyQt5 import uic


class ProgressDialog(QDialog):
    """Displays a progress dialog while a thread is running. When the thread
    stops, the dialog disappears.

    Args:
        thread (thread) the thread to execute."""
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
