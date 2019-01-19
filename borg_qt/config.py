import os
import configparser
import json

from helper import BorgException


class Config():
    def __init__(self):
        self.list_values = ['excludes', 'includes']

    def _get_path(self):
        home = os.environ['HOME']
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if os.path.exists(os.path.join(home, '.config/borg_qt/borg_qt.conf')):
            return os.path.join(home, '.config/borg_qt/borg_qt.conf')
        elif os.path.exists(os.path.join(dir_path, 'borg_qt.conf')):
            return os.path.join(dir_path, 'borg_qt.conf')
        else:
            raise BorgException("Configuration file not found!")

    def _set_environment_variables(self):
        os.environ['BORG_REPO'] = str(self.repository_path)
        os.environ['BORG_PASSPHRASE'] = str(self.password)

    def _create_server_path(self):
        if not self.config['borgqt']['user']:
            raise BorgException("User is missing in config.")
        if not self.config['borgqt']['port']:
            raise BorgException("Port is missing in config.")
        server_path = (self.config['borgqt']['user']
                       + "@"
                       + self.config['borgqt']['server']
                       + ":"
                       + self.config['borgqt']['port']
                       + self.config['borgqt']['repository_path'])
        return server_path

    def read(self):
        """Reads the config file
        """
        self.path = self._get_path()
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def apply(self):
        for option, value in self.config.items('borgqt'):
            setattr(self, option, value)

        for item in self.list_values:
            setattr(self, item, json.loads(
                self.config['borgqt'].get(item, '[]')))

        if self.config['borgqt']['server']:
            self.repository_path = self._create_server_path()
        self._set_environment_variables()

    def write(self):
        if self.server:
            self.config['borgqt']['port'] = self.port
            self.config['borgqt']['user'] = self.user
            self.config['borgqt']['server'] = self.server

        for item in self.list_values:
            self.config['borgqt'][item] = json.dumps(
                getattr(self, item), indent=4, sort_keys=True)

        self.config['borgqt']['password'] = self.password
        with open(self.path, 'w+') as configfile:
            self.config.write(configfile)
