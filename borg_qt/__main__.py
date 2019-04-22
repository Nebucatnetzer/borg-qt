#!/usr/bin/env python

import sys
from PyQt5.QtWidgets import QApplication

from borg_qt.main_window import MainWindow
from borg_qt.helper import get_parser


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    parser = get_parser()
    args = parser.parse_args()

    # only show the application if there's no background flag
    if args.background:
        window.background_backup()
    else:
        window.show()
        window.start()

        sys.exit(app.exec_())
