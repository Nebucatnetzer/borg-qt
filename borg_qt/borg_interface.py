import subprocess
import json

from PyQt5.QtCore import QThread

from helper import BorgException
from progress import ProgressDialog


def _process_json_error(json_err):
    if json_err:
        error = json_err.splitlines()[0]
        if 'stale' in error:
            pass
        else:
            err = json.loads(error)
            raise BorgException(err['message'])


def _process_json_archives(json_output):
    archives = []
    if json_output:
        output = json.loads(json_output)
        for i in output['archives']:
            archives.append(i)
    return archives


def _process_json_repo_stats(json_output):
    if json_output:
        output = json.loads(json_output)
        stats = output['cache']['stats']
        return stats


def _get_json_archives():
    p = subprocess.Popen(['borg', 'list', '--log-json', '--json'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         encoding='utf8')
    json_output, json_err = p.communicate()
    _process_json_error(json_err)
    return json_output


def _process_prefix(prefix):
    if prefix:
        return prefix + "_"
    else:
        return ""


def _process_includes(includes):
    return ' '.join(includes)


def _process_excludes(excludes):
    if excludes:
        processed_items = []
        for item in excludes:
            processed_items.append('--exclude=' + '"' + item + '"')
        return ' '.join(processed_items)
    else:
        return ""


class BackupThread(QThread):
    def __init__(self, includes, excludes=None, prefix=None):
        super().__init__()
        self.includes = _process_includes(includes)
        self.excludes = _process_excludes(excludes)
        self.prefix = _process_prefix(prefix)

    def stop(self):
        self.p.kill()
        self.json_err = None

    def run(self):
        """Function to create a backup with borg.

        Args:
            prefix (str) the prefix for the archive name.
            raw_includes (list) a list of all the paths to backup.
            raw_excludes (list) a list of all the paths to exclude from the backup.
        """
        self.p = subprocess.Popen(['borg', 'create', '--log-json', '--json',
                                   ('::'
                                    + self.prefix
                                    + '{now:%Y-%m-%d_%H:%M:%S}'),
                                   self.includes,
                                   self.excludes],
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  encoding='utf8')
        self.json_output, self.json_err = self.p.communicate()
        self.p.wait()
        _process_json_error(self.json_err)


def backup(includes, excludes=None, prefix=None):
    thread = BackupThread(includes, excludes=excludes, prefix=prefix)
    dialog = ProgressDialog(thread)
    dialog.label_info.setText("creating a backup.")
    dialog.exec_()


def background_backup(includes, excludes=None, prefix=None):
    thread = BackupThread(includes, excludes=excludes, prefix=prefix)
    thread.run()


def get_archives():
    """Returns a list of all the archives in the repository."""
    return _process_json_archives(_get_json_archives())


def get_repository_stats():
    p = subprocess.Popen(['borg', 'info', '--log-json', '--json'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         encoding='utf8')
    json_output, json_err = p.communicate()
    _process_json_error(json_err)
    return _process_json_repo_stats(json_output)
