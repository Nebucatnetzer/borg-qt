import os
import math
from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QDesktopServices


class BorgException(Exception):
    pass


def show_error(e):
    """Helper function to show an error dialog."""
    message = QMessageBox()
    message.setIcon(QMessageBox.Warning)
    message.setText("Error")
    message.setWindowTitle("Borg-Qt Error")
    message.setInformativeText(e.args[0])
    message.exec_()


# taken from here: https://stackoverflow.com/a/14822210/7723859
def convert_size(size_bytes):
    """A function to display file sizes in human readable form."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1000, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def open_path(target_path):
    """Opens the file manager at the given location."""
    if os.path.exists(target_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(
            os.path.abspath(target_path)))
