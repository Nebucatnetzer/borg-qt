import os

import unittest
import warnings

from main_window import MainWindow


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
