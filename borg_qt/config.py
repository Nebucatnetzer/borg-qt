import os
import configparser
import json
from distutils import util
from datetime import datetime
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5 import uic

from borg_qt.helper import BorgException
from borg_qt.systemd import SystemdFile


class Config(QDialog):
    """A class to read, display and write the Borg-Qt configuration."""

    def __init__(self):
        super(QDialog, self).__init__()
        # Load the UI file to get the dialogs layout.
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/Settings.ui')
        uic.loadUi(ui_path, self)

        # Connect all the button and actions.
        self.button_box.accepted.connect(self.accept)
        self.button_include_file.clicked.connect(self.include_file)
        self.button_include_directory.clicked.connect(self.include_directory)
        self.button_exclude_file.clicked.connect(self.exclude_file)
        self.button_exclude_directory.clicked.connect(self.exclude_directory)
        self.button_remove_include.clicked.connect(self.remove_include)
        self.button_remove_exclude.clicked.connect(self.remove_exclude)
        self.button_restore_exclude_defaults.clicked.connect(
            self.restore_exclude_defaults)

        weekdays = ['', 'Monday', 'Thuesday', 'Weekdays', 'Thursday', 'Friday',
                    'Saturday', 'Sunday']
        self.combo_schedule_weekday.addItems(weekdays)
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November',
                  'December']
        self.combo_schedule_month.addItems(months)
        schedules = ['hourly', 'daily', 'weekly', 'monthly']
        self.combo_schedule_predefined.addItems(schedules)

    @property
    def full_path(self):
        """returns the repository path or the repository server path if a
        server was provided in the configuration."""
        if self._return_single_option('repository_path'):
            if self._return_single_option('server'):
                return self._create_server_path()
            else:
                return self._return_single_option('repository_path')
        else:
            return ""

    @property
    def repository_path(self):
        return self._return_single_option('repository_path')

    @property
    def password(self):
        return self._return_single_option('password')

    @property
    def includes(self):
        return self._return_list_option('includes')

    @property
    def excludes(self):
        return self._return_list_option('excludes')

    @property
    def server(self):
        return self._return_single_option('server')

    @property
    def port(self):
        return self._return_single_option('port')

    @property
    def user(self):
        return self._return_single_option('user')

    @property
    def prefix(self):
        return self._return_single_option('prefix')

    @property
    def schedule_enabled(self):
        return util.strtobool(self._return_single_option('schedule_enabled'))

    @property
    def schedule_predefined_enabled(self):
        return util.strtobool(
            self._return_single_option('schedule_predefined_enabled'))

    @property
    def schedule_custom_enabled(self):
        return util.strtobool(
            self._return_single_option('schedule_custom_enabled'))

    @property
    def schedule_time(self):
        return self._return_single_option('schedule_time')

    @property
    def schedule_weekday(self):
        return int(self._return_single_option('schedule_weekday'))

    @property
    def schedule_month(self):
        return int(self._return_single_option('schedule_month'))

    @property
    def schedule_date(self):
        return int(self._return_single_option('schedule_date'))

    @property
    def schedule_predefined_name(self):
        return self._return_single_option('schedule_predefined_name')

    @property
    def hide_help(self):
        return util.strtobool(self._return_single_option('hide_help'))

    def _return_single_option(self, option):
        """Gets the provided option from the configparser object."""
        if option in self.config['borgqt']:
            return self.config['borgqt'][option]
        else:
            return ""

    def _return_list_option(self, option):
        """Reads the provided option from the configparser object and returns
        it as a list."""
        if option in self.config['borgqt']:
            return json.loads(self.config['borgqt'][option])
        else:
            return []

    def _get_path(self):
        """searches for the configuration file and returns its full path."""
        home = os.environ['HOME']
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if os.path.exists(os.path.join(home, '.config/borg_qt/borg_qt.conf')):
            return os.path.join(home, '.config/borg_qt/borg_qt.conf')
        elif os.path.exists(os.path.join(dir_path, 'borg_qt.conf')):
            return os.path.join(dir_path, 'borg_qt.conf')
        else:
            raise BorgException("Configuration file not found!")

    def _set_environment_variables(self):
        os.environ['BORG_REPO'] = self.full_path
        os.environ['BORG_PASSPHRASE'] = self.password

    def _create_server_path(self):
        """creates the full server path from the server, user and port
        options."""
        if not self._return_single_option('user'):
            raise BorgException("User is missing in config.")
        if not self._return_single_option('port'):
            raise BorgException("Port is missing in config.")
        server_path = ('ssh://'
                       + self.config['borgqt']['user']
                       + "@"
                       + self.config['borgqt']['server']
                       + ":"
                       + self.config['borgqt']['port']
                       + self.config['borgqt']['repository_path'])
        return server_path

    def _select_file(self):
        """Qt dialog to select an exisiting file."""
        dialog = QFileDialog
        dialog.ExistingFile
        file_path, _ = dialog.getOpenFileName(
            self, "Select Directory", os.getenv('HOME'), "All Files (*)")
        return file_path

    def _select_directory(self):
        """Qt dialog to select directories."""
        dialog = QFileDialog
        dialog.DirectoryOnly
        return dialog.getExistingDirectory(
            self, "Select Directory", os.getenv('HOME'))

    def _create_service(self):
        self.service = SystemdFile('borg_qt.service')
        self.service.content['Service'] = {}
        self.service.content['Unit']['Description'] = ("Runs Borg-Qt once in "
                                                       "the backround to take "
                                                       "a backup according to "
                                                       "the configuration.")
        self.service.content['Service']['Type'] = 'oneshot'
        process = subprocess.run(["which", "borg_qt"], stdout=subprocess.PIPE,
                                 encoding='utf8')
        output = process.stdout.strip()
        self.service.content['Service']['ExecStart'] = output + ' -B'
        self.service.write()

    def _create_timer(self, schedule_interval):
        self.timer = SystemdFile('borg_qt.timer')
        self.timer.content['Timer'] = {}
        self.timer.content['Install'] = {}
        self.timer.content['Unit']['Description'] = ("Starts the "
                                                     "borg_qt.service "
                                                     "according to the "
                                                     "configured "
                                                     "schedule.")
        self.timer.content['Timer']['OnCalendar'] = schedule_interval
        self.timer.content['Timer']['Persistent'] = 'true'
        self.timer.content['Install']['WantedBy'] = 'timers.target'
        self.timer.write()

    def _parse_schedule_interval(self):
        if self.schedule_predefined_enabled:
            return self.schedule_predefined_name
        if self.schedule_custom_enabled:
            if self.schedule_date > 0:
                date = str(self.schedule_date)
            else:
                date = "*"
            if self.schedule_month > 0:
                month = str(self.schedule_month)
            else:
                month = "*"
            if self.schedule_weekday > 0:
                weekday = self.combo_schedule_weekday.currentText()
            else:
                weekday = ""

            date_string = (weekday
                           + " "
                           + "*"
                           + "-"
                           + month
                           + "-"
                           + date
                           + " "
                           + self.schedule_time)
            return date_string

    def include_file(self):
        """add a file to the include list if the selected path is not empty."""
        file_path = self._select_file()
        if file_path:
            self.list_include.addItem(file_path)

    def include_directory(self):
        """add a directory to the include list if the selected path is not
        empty."""
        directory_path = self._select_directory()
        if directory_path:
            self.list_include.addItem(directory_path)

    def exclude_file(self):
        """add a file to the exclude list if the selected path is not empty."""
        file_path = self._select_file()
        if file_path:
            self.list_exclude.addItem(file_path)

    def exclude_directory(self):
        """add a file to the exclude list if the selected path is not empty."""
        directory_path = self._select_directory()
        if directory_path:
            self.list_exclude.addItem(directory_path)

    def remove_include(self):
        self.list_include.takeItem(self.list_include.currentRow())

    def remove_exclude(self):
        self.list_exclude.takeItem(self.list_exclude.currentRow())

    def restore_exclude_defaults(self):
        self.list_exclude.clear()
        default_excludes = json.loads(self.config['DEFAULT']['excludes'])
        self.list_exclude.addItems(default_excludes)

    def read(self):
        """Reads the config file"""
        self.path = self._get_path()
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def set_form_values(self):
        # set the general tab values
        self.line_edit_repository_path.setText(self.repository_path)
        self.line_edit_password.setText(self.password)
        self.line_edit_prefix.setText(self.prefix)
        self.line_edit_server.setText(self.server)
        self.line_edit_port.setText(self.port)
        self.line_edit_user.setText(self.user)
        # set the include tab values
        self.list_include.clear()
        self.list_include.addItems(self.includes)
        # set the include tab values
        self.list_exclude.clear()
        self.list_exclude.addItems(self.excludes)
        # set schedule tab values
        if self.schedule_enabled:
            self.check_schedule_enabled.setChecked(True)
        if self.schedule_custom_enabled:
            self.radio_schedule_custom_enabled.setChecked(True)
        _time = datetime.strptime(self.schedule_time, '%H:%M:%S')
        self.time_schedule_time.setTime(_time.time())
        self.combo_schedule_weekday.setCurrentIndex(self.schedule_weekday)
        self.combo_schedule_month.setCurrentIndex(self.schedule_month)
        index = self.combo_schedule_predefined.findText(
            self.schedule_predefined_name, Qt.MatchFixedString)
        self.combo_schedule_predefined.setCurrentIndex(index)
        self.spin_schedule_date.setValue(self.schedule_date)

    def apply_options(self):
        """Writes the changed options back into the configparser object."""
        self.config['borgqt']['repository_path'] = (
            self.line_edit_repository_path.text())
        self.config['borgqt']['password'] = self.line_edit_password.text()
        self.config['borgqt']['prefix'] = self.line_edit_prefix.text()
        self.config['borgqt']['server'] = self.line_edit_server.text()
        self.config['borgqt']['port'] = self.line_edit_port.text()
        self.config['borgqt']['user'] = self.line_edit_user.text()
        self.config['borgqt']['schedule_enabled'] = (
            str(self.check_schedule_enabled.isChecked()))
        self.config['borgqt']['schedule_predefined_enabled'] = (
            str(self.radio_schedule_predefined_enabled.isChecked()))
        self.config['borgqt']['schedule_custom_enabled'] = (
            str(self.radio_schedule_custom_enabled.isChecked()))
        self.config['borgqt']['schedule_time'] = (
            self.time_schedule_time.time().toString())
        self.config['borgqt']['schedule_weekday'] = (
            str(self.combo_schedule_weekday.currentIndex()))
        self.config['borgqt']['schedule_month'] = (
            str(self.combo_schedule_month.currentIndex()))
        self.config['borgqt']['schedule_date'] = self.spin_schedule_date.text()
        self.config['borgqt']['schedule_predefined_name'] = (
            self.combo_schedule_predefined.currentText())

        # Workaraound to get all items of a QListWidget as a list
        excludes = []
        for index in range(self.list_exclude.count()):
            excludes.append(self.list_exclude.item(index).text())

        # Workaraound to get all items of a QListWidget as a list
        includes = []
        for index in range(self.list_include.count()):
            includes.append(self.list_include.item(index).text())

        # Configparser doesn't know about list therefore we store them as json
        # strings
        self.config['borgqt']['includes'] = json.dumps(includes,
                                                       indent=4,
                                                       sort_keys=True)
        self.config['borgqt']['excludes'] = json.dumps(excludes,
                                                       indent=4,
                                                       sort_keys=True)
        self._set_environment_variables()

        # create and enable the required systemd files
        # if it is not enable make sure that the timer is disabled.
        if self.schedule_enabled:
            self._create_service()
            self._create_timer(self._parse_schedule_interval())
            self.timer.enable()
        else:
            active_timer_path = os.path.join(
                os.environ['HOME'],
                '.config/systemd/user/timer.targets.wants/borg_qt.timer')
            if os.path.exists(active_timer_path):
                self.timer.disable()

    def write(self):
        """Write the configparser object back to the config file."""
        with open(self.path, 'w+') as configfile:
            self.config.write(configfile)

    def accept(self):
        """Extend the built in accept method to apply and write the new
        options."""
        super().accept()
        self.apply_options()
        self.write()
