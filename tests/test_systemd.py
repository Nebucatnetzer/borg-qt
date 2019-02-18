import os
import unittest

from testcase import TestSystemd

import context
from systemd import SystemdFile


class TestSystemdUnit(TestSystemd):
    def setUp(self):
        self.path = os.path.join(os.environ['HOME'],
                                 '.config/systemd/user/borg_qt.service')

    def test_write_unit(self):
        systemd_unit = SystemdFile('borg_qt.service')
        systemd_unit.write()
        self.assertTrue(os.path.exists(self.path))


class TestSystemdTimer(TestSystemd):
    def setUp(self):
        self.path = os.path.join(os.environ['HOME'],
                                 '.config/systemd/user/borg_qt.timer')

    def test_write_timer(self):
        systemd_timer = SystemdFile('borg_qt.timer')
        systemd_timer.write()
        self.assertTrue(os.path.exists(self.path))


class TestSystemdEnabledTimer(TestSystemd):
    def setUp(self):
        self.symlink_path = os.path.join(os.environ['HOME'],
                                         '.config/systemd/user/timers.target.wants/borg_qt.timer')
        self.path = os.path.join(os.environ['HOME'],
                                 '.config/systemd/user/borg_qt.timer')

    def tearDown(self):
        super().tearDown()
        os.remove(self.symlink_path)

    def test_enable_timer(self):
        systemd_unit = SystemdFile('borg_qt.service')
        systemd_timer = SystemdFile('borg_qt.timer')
        systemd_unit.content['Unit'] = {}
        systemd_unit.content['Unit']['After'] = 'default.target'
        systemd_unit.content['Install'] = {}
        systemd_unit.content['Install']['Wanted'] = 'default.target'
        systemd_unit.content['Service'] = {}
        systemd_unit.content['Service']['Type'] = 'forking'
        systemd_unit.content['Service']['ExecStart'] = '/bin/echo "test"'
        systemd_unit.write()
        systemd_timer.content['Unit'] = {}
        systemd_timer.content['Unit']['Description'] = 'Test Timer'
        systemd_timer.content['Timer'] = {}
        systemd_timer.content['Timer']['OnCalendar'] = 'daily'
        systemd_timer.content['Timer']['Persistent'] = 'true'
        systemd_timer.content['Install'] = {}
        systemd_timer.content['Install']['WantedBy'] = 'timers.target'
        systemd_timer.write()
        systemd_timer.enable()
        self.assertTrue(os.path.exists(self.symlink_path))
