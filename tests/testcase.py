import os
import subprocess
import shutil

import unittest
import warnings

import context
from main_window import MainWindow
from helper import remove_path


def fxn():
    warnings.warn("deprecated", DeprecationWarning)


class BorgQtTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fxn()
            self.form = MainWindow()

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.dir_path,
                                        '../docs/borg_qt.conf.example')


class BorgInterfaceTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.repository_path = '/tmp/test-borgqt'
        os.environ['BORG_REPO'] = self.repository_path
        os.environ['BORG_PASSPHRASE'] = 'foo'
        os.environ['BORG_DISPLAY_PASSPHRASE'] = 'no'
        subprocess.run(['borg', 'init',
                        '--encryption=repokey-blake2'],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

    def tearDown(self):
        remove_path(self.repository_path)


class TestSystemd(unittest.TestCase):
    def tearDown(self):
        os.remove(self.path)
