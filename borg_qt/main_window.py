import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QFileSystemModel

from config import Config
from helper import BorgException, show_error, convert_size
import borg_interface as borg


class MainWindow(QMainWindow):
    """The main window of the application. It provides the various functions to
    control BorgBackup."""
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        QCoreApplication.setApplicationName("borg-qt")

        # Load the UI file to get the dialogs layout.
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/MainWindow.ui')
        uic.loadUi(ui_path, self)

        # Set the window title after the UI has been loaded. Otherwise it gets
        # overwritten.
        self.setWindowTitle("Borg-Qt")

        # Create a Config object for storing the configuration.
        self.config = Config()

        # File tree
        model = QFileSystemModel()
        # model.setRootPath('/')
        model.setRootPath(os.getenv('HOME'))
        self.treeview_files.setModel(model)
        self.treeview_files.expandAll()
        self.treeview_files.setIndentation(20)
        self.treeview_files.setColumnHidden(1, True)
        self.treeview_files.setColumnHidden(2, True)
        self.treeview_files.setColumnHidden(3, True)
        # return the clicking on an item in the tree
        self.treeview_files.clicked.connect(self.get_selected_path)

        self.list_archive.setSortingEnabled(True)

        # Connecting actions and buttons.
        self.action_settings.triggered.connect(self.show_settings)
        self.action_backup.triggered.connect(self.create_backup)

    def start(self):
        """This method is intendet to be used only once at the application
        start. It reads the configuration file and sets the required
        environment variables."""
        try:
            self.config.read()
            self.config._set_environment_variables()
            self._update_archives()
            self._update_repository_stats()
        except BorgException as e:
            show_error(e)
            sys.exit(1)

    def show_settings(self):
        """Display the settings dialog."""
        self.config.set_form_values()
        self.config.exec_()

    def get_selected_path(self, signal):
        """returns the path of the item selected in the file tree."""
        self.src_path = self.treeview_files.model().filePath(signal)

    def _check_path(self):
        message = ("Please select a file or directory "
                   "before creating a backup.")
        if not hasattr(self, 'src_path'):
            raise BorgException(message)

    def create_backup(self):
        """Creates a backup of the selected item in the treeview."""
        try:
            self._check_path()
            borg.backup([self.src_path], excludes=self.config.excludes,
                        prefix=self.config.prefix)
            self.update_archives()
            self.update_repository_stats()
        except BorgException as e:
            show_error(e)

    def _update_archives(self):
        """Lists all the archive names in the UI."""
        self.list_archive.clear()
        archive_names = []
        for archive in borg.get_archives():
            archive_names.append(archive['name'])
        self.list_archive.addItems(archive_names)

    def update_archives(self):
        """Lists all the archive names in the UI."""
        try:
            self._update_archives()
        except BorgException as e:
            show_error(e)

    def _update_repository_stats(self):
        stats = borg.get_repository_stats()
        self.label_repo_original_size.setText(
            "Original Size: "
            + convert_size(stats['total_size']))

        self.label_repo_compressed_size.setText(
            "Compressed Size: "
            + convert_size(stats['total_csize']))

        self.label_repo_deduplicated_size.setText(
            "Deduplicated Size: "
            + convert_size(stats['unique_csize']))

    def update_repository_stats(self):
        try:
            self._update_repository_stats()
        except BorgException as e:
            show_error(e)
