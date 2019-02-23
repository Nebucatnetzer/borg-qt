import configparser
import os
import subprocess


class SystemdFile():
    def __init__(self, file_name):
        self.file_name = file_name
        self.systemd_folder = os.path.join(os.environ['HOME'],
                                           '.config/systemd/user/')
        self.path = os.path.join(self.systemd_folder,
                                 self.file_name)
        self.content = configparser.ConfigParser()
        self.content.optionxform = str
        self.content['Unit'] = {}

    def write(self):
        try:
            os.makedirs(self.systemd_folder)
        except OSError:
            pass
        with open(self.path, 'w+') as configfile:
            self.content.write(configfile)

    def enable(self):
        subprocess.run(['systemctl', '--user', 'daemon-reload'])
        subprocess.run(['systemctl', '--user', 'enable',
                        self.file_name])
        subprocess.run(['systemctl', '--user', 'restart',
                        self.file_name])

    def disable(self):
        subprocess.run(['systemctl', '--user', 'disable',
                        self.file_name])
        subprocess.run(['systemctl', '--user', 'stop',
                        self.file_name])
