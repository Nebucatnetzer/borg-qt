import os
import shutil
import subprocess
import json

from PyQt5.QtCore import QThread

from helper import BorgException


class BorgQtThread(QThread):
    def __init__(self):
        super().__init__()
        self.create_pocess()

    def stop(self):
        self.p.kill()
        self.json_err = None

    def create_pocess(self):
        self.create_command()
        self.p = subprocess.Popen(self.command,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf8')

    def run(self):
        self.json_output, self.json_err = self.p.communicate()
        self.p.wait()
        self.process_json_error(self.json_err)

    def process_json_error(self, json_err):
        if json_err:
            error = json_err.splitlines()[0]
            if 'stale' in error:
                pass
            else:
                err = json.loads(error)
                raise BorgException(err['message'])


class ListThread(BorgQtThread):
    def create_command(self):
        self.command = ['borg', 'list', '--log-json', '--json']

    def run(self):
        super().run()
        self._process_json_archives()
        return self.archives

    def _process_json_archives(self):
        self.archives = []
        if self.json_output:
            output = json.loads(self.json_output)
            for i in output['archives']:
                self.archives.append(i)


class InfoThread(BorgQtThread):
    def create_command(self):
        self.command = ['borg', 'info', '--log-json', '--json']

    def run(self):
        super().run()
        self._process_json_repo_stats()
        return self.stats

    def _process_json_repo_stats(self):
        if self.json_output:
            output = json.loads(self.json_output)
            self.stats = output['cache']['stats']


class BackupThread(BorgQtThread):
    """A class to create a backup with borg.

    Args:
        prefix (str) the prefix for the archive name.
        includes (list) a list of all the paths to backup.
        excludes (list) a list of all the paths to exclude from the backup.
    """
    def __init__(self, includes, excludes=None, prefix=None):
        self.includes = includes
        self._process_excludes(excludes)
        self._process_prefix(prefix)
        super().__init__()

    def create_command(self):
        self.command = ['borg', 'create', '--log-json', '--json',
                        ('::'
                         + self.prefix
                         + '{now:%Y-%m-%d_%H:%M:%S}')]
        self.command.extend(self.includes)
        if self.excludes:
            self.command.extend(self.excludes)

    def _process_prefix(self, prefix):
        if prefix:
            self.prefix = prefix + "_"
        else:
            self.prefix = ""

    def _process_excludes(self, excludes):
        processed_items = []
        if excludes:
            for item in excludes:
                processed_items.extend(['-e', item])
            self.excludes = processed_items
        else:
            self.excludes = processed_items


class RestoreThread(BorgQtThread):
    """A lass to restore a backup with borg.

    Args:
        archive_name (str) the name of the archive to restore.
        restore_path (str) the path where to restore should get stored at.
    """
    def __init__(self, archive_name, restore_path):
        self.archive_name = archive_name
        self.restore_path = restore_path
        super().__init__()

    def create_command(self):
        self.command = ['borg', 'extract', '--log-json',
                        ('::' + self.archive_name)]

    def create_pocess(self):
        self.create_command()
        self.p = subprocess.Popen(self.command,
                                  cwd=self.restore_path,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf8')


class DeleteThread(BorgQtThread):
    """A lass to restore a backup with borg.

    Args:
        archive_name (str) the name of the archive to restore.
    """
    def __init__(self, archive_name):
        self.archive_name = archive_name
        super().__init__()

    def create_command(self):
        self.command = ['borg', 'delete', '--log-json',
                        ('::' + self.archive_name)]


class MountThread(BorgQtThread):
    """A lass to restore a backup with borg.

    Args:
        archive_name (str) the name of the archive to restore.
    """
    def __init__(self, archive_name, mount_path):
        self.archive_name = archive_name
        self.mount_path = mount_path
        super().__init__()

    def create_command(self):
        self.command = ['borg', 'mount', '--log-json',
                        ('::' + self.archive_name), self.mount_path]
