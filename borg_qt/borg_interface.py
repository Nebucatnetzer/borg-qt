import subprocess
import json

from PyQt5.QtCore import QThread

from borg_qt.helper import BorgException, show_error


class BorgQtThread(QThread):
    """Provides the base for interfacing with borg. The method
    self.create_command needs to be implemented on each child class in order to
    make it work."""
    def __init__(self):
        super().__init__()
        self.create_process()

    def stop(self):
        """Kill the process when the thread stops."""
        self.p.kill()
        self.json_err = None

    def create_process(self):
        """Creates the process which executes borg."""

        # self.create_command() needs to be implemented on each subclass.
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
        """Looks in the returned json error string for errors and provides them
        as BorgException in case there are any. Ignores errors about stale
        locks of borg."""
        if json_err:
            error = json_err.splitlines()[0]
            if 'stale' in error:
                return
            else:
                err = json.loads(error)
                raise BorgException(err['message'])


class ListThread(BorgQtThread):
    """Returns a list of all archives in the repository."""
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
    """Return the statistics about the current repository."""
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
    """Creates a backup with borg.

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
                         + '{now:%Y-%m-%d_%H:%M:%S,%f}')]
        self.command.extend(self.includes)
        if self.excludes:
            self.command.extend(self.excludes)

    def run(self):
        self.json_output, self.json_err = self.p.communicate()
        self.p.wait()
        try:
            self.process_json_error(self.json_err)
        except BorgException as e:
            show_error(e)
            self.stop()

    def _process_prefix(self, prefix):
        """Prepares the prefix for the final command."""
        if prefix:
            self.prefix = prefix + "_"
        else:
            self.prefix = ""

    def _process_excludes(self, excludes):
        """Pairs every exclude with the required option for borg."""
        processed_items = []
        if excludes:
            for item in excludes:
                processed_items.extend(['-e', item])
            self.excludes = processed_items
        else:
            self.excludes = processed_items


class RestoreThread(BorgQtThread):
    """Restores a backup with borg.

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

    def create_process(self):
        """The create_process needs to get overwritten because borg restores
        the archive into the current folder. Therefore the process needs to cd
        into the target path."""
        self.create_command()
        self.p = subprocess.Popen(self.command,
                                  cwd=self.restore_path,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf8')


class DeleteThread(BorgQtThread):
    """Deletes an archive from the repository.

    Args:
        archive_name (str) the name of the archive to delete.
    """
    def __init__(self, archive_name):
        self.archive_name = archive_name
        super().__init__()

    def create_command(self):
        self.command = ['borg', 'delete', '--log-json',
                        ('::' + self.archive_name)]


class MountThread(BorgQtThread):
    """Mounts an archive at the given path.

    Args:
        archive_name (str) the name of the archive to restore.
        mount_path (str) the target path to mount the archive at.
    """
    def __init__(self, archive_name, mount_path):
        self.archive_name = archive_name
        self.mount_path = mount_path
        super().__init__()

    def create_command(self):
        self.command = ['borg', 'mount', '--log-json',
                        ('::' + self.archive_name), self.mount_path]


class PruneThread(BorgQtThread):
    """Prunes the repository according to the given retention policy.

    Args:
        policy (dict) the name of the archive to restore.
    """
    def __init__(self, policy):
        self.policy = self._process_policy(policy)
        super().__init__()

    def create_command(self):
        self.command = ['borg', 'prune', '--log-json']
        self.command.extend(self.policy)

    def _process_policy(self, raw_policy):
        policy = []
        for key, value in raw_policy.items():
            policy.append('--keep-' + key + "=" + value)
        return policy
