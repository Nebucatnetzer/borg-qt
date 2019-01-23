import os
import sys
import configparser
import unittest
from unittest.mock import MagicMock, patch
import warnings

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

import context
from main_window import MainWindow
from config import Config
from helper import BorgException


app = QApplication(sys.argv)


def fxn():
    warnings.warn("deprecated", DeprecationWarning)


class BorgQtConfigTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fxn()
            self.form = MainWindow()

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.dir_path,
                                        '../docs/borg_qt.conf.example')


class TestConfiguration(BorgQtConfigTestCase):
    def test_read_configuration(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        parser = configparser.ConfigParser()
        parser.read(self.config_path)
        self.assertEqual(parser, self.form.config.config)

    @patch('config.os.path')
    def test_absent_config_file(self, mock_path):
        mock_path.exists.return_value = False
        with self.assertRaises(BorgException):
            self.form.config._get_path()

    def test_absent_port(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        self.form.config.config['borgqt']['port'] = ""
        with self.assertRaises(BorgException):
            self.form.config._create_server_path()

    def test_absent_user(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        self.form.config.config['borgqt']['user'] = ""
        with self.assertRaises(BorgException):
            self.form.config._create_server_path()

    def test_apply_settings(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        self.form.config.apply_options()
        self.assertIs(type(self.form.config.excludes), list)
        self.assertEqual(self.form.config.full_path,
                         os.environ['BORG_REPO'])
        self.assertEqual(self.form.config.password,
                         os.environ['BORG_PASSPHRASE'])


class TestWriteConfiguration(BorgQtConfigTestCase):
    def tearDown(self):
        if os.path.exists(self.form.config.path):
            os.remove(self.form.config.path)

    def test_write_config(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        self.form.config.path = '/tmp/test.conf'
        self.form.config.write()
        config = configparser.ConfigParser()
        config.read(self.form.config.path)
        self.assertEqual(self.form.config.config['borgqt']['password'],
                         config['borgqt']['password'])


class TestGuiConfiguration(BorgQtConfigTestCase):
    def setUp(self):
        super().setUp()
        self.form.config.read()
        self.form.config.path = '/tmp/test.conf'

    def tearDown(self):
        if os.path.exists(self.form.config.path):
            os.remove(self.form.config.path)

    def test_set_form_values(self):
        self.form.config.set_form_values()
        self.assertEqual(self.form.config.password,
                         self.form.config.line_edit_password.text())

    def test_cancel_settings(self):
        self.form.config.line_edit_password.clear()
        QTest.keyClicks(self.form.config.line_edit_password, "bar")
        cancel_button = self.form.config.button_box.button(
            self.form.config.button_box.Cancel)
        QTest.mouseClick(cancel_button, Qt.LeftButton)
        self.assertEqual(self.form.config.password,
                         self.form.config.config['borgqt']['password'])

    def test_ok_settings(self):
        self.form.config.line_edit_password.clear()
        QTest.keyClicks(self.form.config.line_edit_password, "bar")
        ok_button = self.form.config.button_box.button(
            self.form.config.button_box.Ok)
        QTest.mouseClick(ok_button, Qt.LeftButton)
        parser = configparser.ConfigParser()
        parser.read(self.form.config.path)
        self.assertEqual(self.form.config.line_edit_password.text(),
                         parser['borgqt']['password'])

    def test_include_remove(self):
        self.form.config.set_form_values()
        counter = self.form.config.list_include.count()
        self.form.config.list_include.setCurrentRow(0)
        self.form.config.remove_include()
        self.assertGreaterEqual(counter, self.form.config.list_include.count())

    def test_exclude_remove(self):
        self.form.config.set_form_values()
        counter = self.form.config.list_exclude.count()
        self.form.config.list_exclude.setCurrentRow(0)
        self.form.config.remove_exclude()
        self.assertGreaterEqual(counter, self.form.config.list_exclude.count())
