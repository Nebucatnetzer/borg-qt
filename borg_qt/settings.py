import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic


class Settings(QDialog):
    def __init__(self, config):
        super(QDialog, self).__init__()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/Settings.ui')
        uic.loadUi(ui_path, self)
        self.config = config

        self.read_config()
        self.button_box.accepted.connect(self.read_inputs)
        self.show()

    def read_config(self):
        try:
            self.line_edit_repository_path.setText(self.config.repository_path)
            self.line_edit_password.setText(self.config.password)
        except AttributeError:
            pass
        try:
            self.line_edit_prefix.setText(self.config.prefix)
        except AttributeError:
            pass
        try:
            self.line_edit_server.setText(self.config.server)
            self.line_edit_port.setText(self.config.port)
            self.line_edit_user.setText(self.config.user)
        except AttributeError:
            pass

        try:
            self.list_include.clear()
            self.list_include.addItems(self.config.includes)
        except AttributeError:
            pass
        try:
            self.list_exclude.clear()
            self.list_exclude.addItems(self.config.excludes)
        except AttributeError:
            pass

    def read_inputs(self):
        self.config.repository_path = self.line_edit_repository_path.text()
        self.config.password = self.line_edit_password.text()
        self.config.prefix = self.line_edit_prefix.text()
        self.config.server = self.line_edit_server.text()
        self.config.port = self.line_edit_port.text()
        self.config.user = self.line_edit_user.text()

        excludes = []
        for index in range(self.list_exclude.count()):
            excludes.append(self.list_exclude.item(index).text())

        includes = []
        for index in range(self.list_include.count()):
            includes.append(self.list_include.item(index).text())

        self.config.includes = includes
        self.config.excludes = excludes
        self.config.write()
        self.config.apply()
