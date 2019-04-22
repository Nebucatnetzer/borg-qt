import os

from borg_qt.systemd import SystemdFile


def test_write_unit(mock_home, monkeypatch):
    monkeypatch.setattr(os, 'environ', mock_home)
    systemd_unit = SystemdFile('borg_qt.service')
    systemd_unit.write()
    assert os.path.exists(systemd_unit.path)


def test_write_timer(mock_home, monkeypatch):
    monkeypatch.setattr(os, 'environ', mock_home)
    systemd_timer = SystemdFile('borg_qt.timer')
    systemd_timer.write()
    assert os.path.exists(systemd_timer.path)


# This test currently runs against the real home directory of the current user.
# Since this can cause problems with a productive Borg-Qt setup I'm commenting
# out this test for the moment. The long time target is to replace it with a
# test which mocks the call to systemd.
#
# class TestSystemdEnabledTimer():
#     def setup_method(self):
#         self.unit_path = os.path.join(os.environ['HOME'],
#                                       '.config/systemd/user/borg_qt.service')
#         self.timer_path = os.path.join(os.environ['HOME'],
#                                       '.config/systemd/user/borg_qt.timer')
#         self.symlink_path = os.path.join(os.environ['HOME'],
#                                          '.config/systemd/user/timers.target.wants/borg_qt.timer')

#     def teardown_method(self):
#         if os.path.exists(self.unit_path):
#             os.remove(self.unit_path)
#         if os.path.exists(self.symlink_path):
#             os.remove(self.symlink_path)
#         if os.path.exists(self.timer_path):
#             os.remove(self.timer_path)

#     def test_enable_timer(self):
#         systemd_unit = SystemdFile('borg_qt.service')
#         systemd_unit.path = self.unit_path
#         systemd_timer = SystemdFile('borg_qt.timer')
#         systemd_timer.path = self.timer_path
#         systemd_unit.content['Unit'] = {}
#         systemd_unit.content['Unit']['After'] = 'default.target'
#         systemd_unit.content['Install'] = {}
#         systemd_unit.content['Install']['Wanted'] = 'default.target'
#         systemd_unit.content['Service'] = {}
#         systemd_unit.content['Service']['Type'] = 'forking'
#         systemd_unit.content['Service']['ExecStart'] = '/bin/echo "test"'
#         systemd_unit.write()
#         systemd_timer.content['Unit'] = {}
#         systemd_timer.content['Unit']['Description'] = 'Test Timer'
#         systemd_timer.content['Timer'] = {}
#         systemd_timer.content['Timer']['OnCalendar'] = 'daily'
#         systemd_timer.content['Timer']['Persistent'] = 'true'
#         systemd_timer.content['Install'] = {}
#         systemd_timer.content['Install']['WantedBy'] = 'timers.target'
#         systemd_timer.write()
#         systemd_timer.enable()
#         assert os.path.exists(self.symlink_path)
