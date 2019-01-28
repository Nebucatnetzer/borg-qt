import os
import sys
import configparser
import unittest
from unittest.mock import MagicMock, patch
import warnings
from shutil import copyfile


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

import context
from main_window import MainWindow
from helper import BorgException
from testcase import BorgQtTestCase


app = QApplication(sys.argv)


class TestConfiguration(BorgQtTestCase):
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

    def test_empty_port(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        self.form.config.config['borgqt']['port'] = ""
        with self.assertRaises(BorgException):
            self.form.config._create_server_path()

    def test_absent_port(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        if 'port' in self.form.config.config['DEFAULT']:
            self.form.config.config['DEFAULT'].pop('port', None)
        if 'port' in self.form.config.config['borgqt']:
            self.form.config.config['borgqt'].pop('port', None)
        with self.assertRaises(BorgException):
            self.form.config._create_server_path()

    def test_empty_user(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        self.form.config.config['borgqt']['user'] = ""
        with self.assertRaises(BorgException):
            self.form.config._create_server_path()

    def test_absent_user(self):
        self.form.config._get_path = MagicMock(return_value=self.config_path)
        self.form.config.read()
        if 'user' in self.form.config.config['DEFAULT']:
            self.form.config.config['DEFAULT'].pop('user', None)
        if 'user' in self.form.config.config['borgqt']:
            self.form.config.config['borgqt'].pop('user', None)
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


class TestWriteConfiguration(BorgQtTestCase):
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


class TestGuiConfiguration(BorgQtTestCase):
    def setUp(self):
        super().setUp()
        copyfile(self.config_path, '/tmp/test.conf')
        self.form.config._get_path = MagicMock(return_value='/tmp/test.conf')
        self.form.config.read()

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
