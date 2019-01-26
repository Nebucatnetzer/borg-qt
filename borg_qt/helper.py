from PyQt5.QtWidgets import QMessageBox


class BorgException(Exception):
    pass


def show_error(e):
    # Error Dialog
    message = QMessageBox()
    message.setIcon(QMessageBox.Warning)
    message.setText("Error")
    message.setWindowTitle("Borg-Qt Error")
    message.setInformativeText(e.args[0])
    message.exec_()
