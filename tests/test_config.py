import unittest
from unittest.mock import MagicMock, patch

import os
import configparser

import context
from config import Config
from helper import BorgException


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.dir_path,
                                        '../docs/borg_qt.conf.example')

    def test_read_configuration(self):
        config = Config()
        config._get_path = MagicMock(return_value=self.config_path)
        config.read()
        parser = configparser.ConfigParser()
        parser.read(self.config_path)
        self.assertEqual(parser, config.config)

    @patch('config.os.path')
    def test_absent_config_file(self, mock_path):
        mock_path.exists.return_value = False
        with self.assertRaises(BorgException):
            config = Config()
            config._get_path()

    def test_absent_port(self):
        config = Config()
        config._get_path = MagicMock(return_value=self.config_path)
        config.read()
        config.config['borgqt']['port'] = ""
        with self.assertRaises(BorgException):
            config._create_server_path()

    def test_absent_port(self):
        config = Config()
        config._get_path = MagicMock(return_value=self.config_path)
        config.read()
        config.config['borgqt']['user'] = ""
        with self.assertRaises(BorgException):
            config._create_server_path()

    def test_apply_settings(self):
        config = Config()
        config._get_path = MagicMock(return_value=self.config_path)
        config.read()
        config.apply()
        self.assertIs(type(config.excludes), list)
        self.assertEqual(str(config.repository_path), os.environ['BORG_REPO'])
        self.assertEqual(str(config.password), os.environ['BORG_PASSPHRASE'])


class TestWriteConfiguration(unittest.TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.dir_path,
                                        '../docs/borg_qt.conf.example')
        self.config = Config()
        self.config._get_path = MagicMock(return_value=self.config_path)
        self.config.read()
        self.config.apply()
        self.config.path = '/tmp/test.conf'

    def tearDown(self):
        os.remove(self.config.path)

    def test_write_config(self):
        self.config.write()
        config = configparser.ConfigParser()
        config.read(self.config.path)
        self.assertEqual(self.config.config['borgqt']['password'],
                         config['borgqt']['password'])
