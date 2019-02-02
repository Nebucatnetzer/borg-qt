import os
import sys
import subprocess
from time import strftime
from unittest.mock import MagicMock
from unittest import TestCase

from PyQt5.QtWidgets import QApplication

import context
from testcase import BorgInterfaceTest
import borg_interface as borg


app = QApplication(sys.argv)


class BackupTestCase(BorgInterfaceTest):
    def test_backup(self):
        borg.backup(['.'])
        output = subprocess.check_output(['borg', 'list'], encoding='utf8')
        self.assertNotEqual(-1, output.find(strftime('%Y-%m-%d_%H:')))

    def test_backup_with_prefix(self):
        borg.backup(['.'], prefix='test')
        output = subprocess.check_output(['borg', 'list'], encoding='utf8')
        self.assertNotEqual(-1, output.find(strftime('test_%Y-%m-%d_%H:')))


class RestoreTestCase(BorgInterfaceTest):
    def setUp(self):
        super().setUp()
        borg.backup(['.'])

    def test_restore(self):
        repo_archives = borg.get_archives()
        archive_name = repo_archives[0]['name']
        target_path = '/tmp/restore/'
        restore_path = os.path.join(target_path, archive_name)
        thread = borg.RestoreThread(archive_name, restore_path)
        thread.run()
        self.assertTrue(os.path.exists(
            os.path.join(restore_path, os.path.realpath(__file__))))


class DeleteTestCase(BorgInterfaceTest):
    def setUp(self):
        super().setUp()
        borg.backup(['.'])

    def test_delete(self):
        repo_archives = borg.get_archives()
        archive_name = repo_archives[0]['name']
        thread = borg.DeleteThread(archive_name)
        thread.run()
        repo_archives = borg.get_archives()
        self.assertEqual(repo_archives, [])
