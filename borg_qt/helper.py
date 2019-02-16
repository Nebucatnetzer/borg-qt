import os
import math
import shutil
from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QDesktopServices


class BorgException(Exception):
    pass


# This was taken from here: https://stackoverflow.com/a/1745965/7723859
def debug_trace():
    '''Set a tracepoint in the Python debugger that works with Qt'''
    from PyQt5.QtCore import pyqtRemoveInputHook

    from pdb import set_trace
    pyqtRemoveInputHook()
    set_trace()


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
    """Opens the file manager at the given location.

    Args:
        target_path (str) The path to open in the file manager."""
    if os.path.exists(target_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(
            os.path.abspath(target_path)))


def create_path(path):
    """Creates the given path.

    Args:
        path (str) The path to create."""
    if not os.path.exists(path):
        os.makedirs(path)


def remove_path(path):
    """Removes the given path recursively.

    Args:
        path (str) The path to delete."""
    if os.path.exists(path):
        shutil.rmtree(path)


def check_path(path):
    """Checks if the given path is writeable.

    Args:
        path (str) The path to check."""
    if os.access(path, os.W_OK):
        return True
    exception = Exception("The selected path isn't writeable!")
    show_error(exception)
