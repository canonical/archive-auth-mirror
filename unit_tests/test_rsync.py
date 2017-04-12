from pathlib import Path
import logging
from subprocess import CalledProcessError
from unittest import TestCase, mock

from fixtures import TestWithFixtures, LoggerFixture

from archive_auth_mirror.rsync import rsync, rsync_multi


class RsyncTest(TestCase):

    @mock.patch('subprocess.check_output')
    def test_rsync(self, mock_check_output):
        """The rsync copies a filesytem tree using rsync."""
        rsync('1.2.3.4', Path('/foo/bar'))
        mock_check_output.assert_called_with(
            ['/usr/bin/rsync', '-a', '/foo/bar', '1.2.3.4:/foo/bar'])

    @mock.patch('subprocess.check_output')
    def test_rsync_delete(self, mock_check_output):
        """If the delete flag is True, the --delete option is passed."""
        rsync('1.2.3.4', Path('/foo/bar'), delete=True)
        mock_check_output.assert_called_with(
            ['/usr/bin/rsync', '-a', '--delete', '/foo/bar',
             '1.2.3.4:/foo/bar'])

    @mock.patch('subprocess.check_output')
    def test_rsync_rsh(self, mock_check_output):
        """If the rsh flag is not None, the --rsh option is passed."""
        rsync('1.2.3.4', Path('/foo/bar'), rsh='ssh -i my-identity')
        mock_check_output.assert_called_with(
            ['/usr/bin/rsync', '-a', '--rsh', 'ssh -i my-identity', '/foo/bar',
             '1.2.3.4:/foo/bar'])


class RsyncMultiTest(TestWithFixtures):

    def setUp(self):
        super().setUp()
        self.logger = self.useFixture(LoggerFixture())

    @mock.patch('subprocess.check_output')
    def test_each_host(self, mock_check_output):
        """The rsync call is performed for each host."""
        rsync_multi(
            ['1.2.3.4', '5.6.7.8'], Path('/foo/bar'), logging.getLogger())
        mock_check_output.assert_has_calls(
            [mock.call(
                ['/usr/bin/rsync', '-a', '/foo/bar', '1.2.3.4:/foo/bar']),
             mock.call(
                 ['/usr/bin/rsync', '-a', '/foo/bar', '5.6.7.8:/foo/bar'])])

    @mock.patch('subprocess.check_output')
    def test_log_failures(self, mock_check_output):
        """If copy to a host fails, it's logged."""

        def check_output(cmd):
            if cmd[-1].startswith('1.2.3.4:'):
                raise CalledProcessError(1, cmd, output='something failed')

        mock_check_output.side_effect = check_output
        rsync_multi(
            ['1.2.3.4', '5.6.7.8'], Path('/foo/bar'), logging.getLogger())
        self.assertIn(
            'rsync to 1.2.3.4 failed: something failed\n', self.logger.output)
        # rsync to the second host is exectuted too
        mock_check_output.assert_any_call(
            ['/usr/bin/rsync', '-a', '/foo/bar', '5.6.7.8:/foo/bar'])

    @mock.patch('subprocess.check_output')
    def test_rsh(self, mock_check_output):
        """The rsh flag is passed through."""
        rsync_multi(
            ['1.2.3.4'], Path('/foo/bar'), logging.getLogger(),
            rsh='ssh -i my-identity')
        mock_check_output.assert_called_with(
            ['/usr/bin/rsync', '-a', '--rsh', 'ssh -i my-identity', '/foo/bar',
             '1.2.3.4:/foo/bar'])
