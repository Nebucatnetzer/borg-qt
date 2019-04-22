import os

from PyQt5.QtWidgets import QDialog
from PyQt5 import uic


class Help(QDialog):
    """A class to display the help dialog."""

    def __init__(self):
        super(QDialog, self).__init__()
        # Load the UI file to get the dialogs layout.
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/Help.ui')
        uic.loadUi(ui_path, self)

        self.button_box.accepted.connect(self.accept)
