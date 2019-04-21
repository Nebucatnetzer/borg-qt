import os
import sys
import configparser

import pytest


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from main_window import MainWindow
from helper import BorgException


app = QApplication(sys.argv)


def test_read_configuration(form):
    parser = configparser.ConfigParser()
    parser.read(form.config.path)
    assert parser == form.config.config


def test_absent_config_file(monkeypatch):
    def mock_path(path):
        return False

    form = MainWindow()
    monkeypatch.setattr(os.path, 'exists', mock_path)
    with pytest.raises(BorgException):
        form.config._get_path()


def test_empty_port(form):
    form.config.config['borgqt']['port'] = ""
    with pytest.raises(BorgException):
        form.config._create_server_path()


def test_absent_port(form):
    if 'port' in form.config.config['DEFAULT']:
        form.config.config['DEFAULT'].pop('port', None)
    if 'port' in form.config.config['borgqt']:
        form.config.config['borgqt'].pop('port', None)
    with pytest.raises(BorgException):
        form.config._create_server_path()


def test_empty_user(form):
    form.config.config['borgqt']['user'] = ""
    with pytest.raises(BorgException):
        form.config._create_server_path()


def test_absent_user(form):
    if 'user' in form.config.config['DEFAULT']:
        form.config.config['DEFAULT'].pop('user', None)
    if 'user' in form.config.config['borgqt']:
        form.config.config['borgqt'].pop('user', None)
    with pytest.raises(BorgException):
        form.config._create_server_path()


def test_apply_settings(form):
    form.config.apply_options()
    assert type(form.config.excludes) == list
    assert form.config.full_path == os.environ['BORG_REPO']
    assert form.config.password == os.environ['BORG_PASSPHRASE']


def test_write_config(form):
    form.config.config['borgqt']['password'] == 'Test String'
    form.config.write()
    config = configparser.ConfigParser()
    config.read(form.config.path)
    for value in config['borgqt']:
        assert (form.config.config['borgqt'][value]
                == config['borgqt'][value])


def test_set_form_values(form):
    form.config.set_form_values()
    assert (form.config.password
            == form.config.line_edit_password.text())


def test_cancel_settings(form):
    form.config.line_edit_password.clear()
    QTest.keyClicks(form.config.line_edit_password, "bar")
    cancel_button = form.config.button_box.button(
        form.config.button_box.Cancel)
    QTest.mouseClick(cancel_button, Qt.LeftButton)
    assert (form.config.password
            == form.config.config['borgqt']['password'])


def test_ok_settings(form):
    form.config.line_edit_password.clear()
    QTest.keyClicks(form.config.line_edit_password, "bar")
    ok_button = form.config.button_box.button(
        form.config.button_box.Ok)
    QTest.mouseClick(ok_button, Qt.LeftButton)
    parser = configparser.ConfigParser()
    parser.read(form.config.path)
    assert (form.config.line_edit_password.text()
            == parser['borgqt']['password'])


def test_include_remove(form):
    form.config.set_form_values()
    counter = form.config.list_include.count()
    form.config.list_include.setCurrentRow(0)
    form.config.remove_include()
    assert (counter >= form.config.list_include.count())


def test_exclude_remove(form):
    form.config.set_form_values()
    counter = form.config.list_exclude.count()
    form.config.list_exclude.setCurrentRow(0)
    form.config.remove_exclude()
    assert (counter >= form.config.list_exclude.count())
