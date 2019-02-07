import os
import sys
import subprocess
from time import strftime

from PyQt5.QtWidgets import QApplication

import context
from testcase import BorgInterfaceTest
import borg_interface as borg
from helper import create_path, remove_path


app = QApplication(sys.argv)


class BackupTestCase(BorgInterfaceTest):
    def test_backup(self):
        self.backup_thread = borg.BackupThread(['.'])
        self.backup_thread.run()
        output = subprocess.check_output(['borg', 'list'], encoding='utf8')
        self.assertNotEqual(-1, output.find(strftime('%Y-%m-%d_%H:')))

    def test_backup_with_prefix(self):
        self.backup_thread = borg.BackupThread(['.'], prefix='test')
        self.backup_thread.run()
        output = subprocess.check_output(['borg', 'list'], encoding='utf8')
        self.assertNotEqual(-1, output.find(strftime('test_%Y-%m-%d_%H:')))


class RestoreTestCase(BorgInterfaceTest):
    def setUp(self):
        super().setUp()
        self.backup_thread = borg.BackupThread(['.'])
        self.backup_thread.run()
        self.target_path = '/tmp/restore/'
        self.list_thread = borg.ListThread()
        repo_archives = self.list_thread.run()
        self.archive_name = repo_archives[0]['name']
        self.restore_path = os.path.join(self.target_path, self.archive_name)
        create_path(self.restore_path)

    def tearDown(self):
        remove_path(self.target_path)
        super().tearDown()

    def test_restore(self):
        thread = borg.RestoreThread(self.archive_name, self.restore_path)
        thread.run()
        self.assertTrue(os.path.exists(
            os.path.join(self.restore_path, os.path.realpath(__file__))))


class DeleteTestCase(BorgInterfaceTest):
    def setUp(self):
        super().setUp()
        self.backup_thread = borg.BackupThread(['.'])
        self.backup_thread.run()
        self.list_thread = borg.ListThread()
        repo_archives = self.list_thread.run()
        self.archive_name = repo_archives[0]['name']

    def test_delete(self):
        thread = borg.DeleteThread(self.archive_name)
        thread.run()
        self.list_thread = borg.ListThread()
        repo_archives = self.list_thread.run()
        self.assertEqual(repo_archives, [])


class MountTestCase(BorgInterfaceTest):
    def setUp(self):
        super().setUp()
        self.backup_thread = borg.BackupThread(['.'])
        self.backup_thread.run()
        self.list_thread = borg.ListThread()
        repo_archives = self.list_thread.run()
        self.archive_name = repo_archives[0]['name']
        self.mount_path = os.path.join('/tmp/', self.archive_name)
        create_path(self.mount_path)

    def tearDown(self):
        os.system('borg umount ' + self.mount_path)
        remove_path(self.mount_path)
        super().tearDown()

    def test_mount(self):
        thread = borg.MountThread(self.archive_name, self.mount_path)
        thread.run()
        self.assertTrue(os.path.exists(
            os.path.join(self.mount_path, os.path.realpath(__file__))))
