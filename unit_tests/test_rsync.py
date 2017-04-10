from pathlib import Path
from unittest import TestCase, mock

from archive_auth_mirror.rsync import rsync


class RsyncTest(TestCase):

    @mock.patch('subprocess.check_call')
    def test_rsync(self, mock_check_call):
        """The rsync copies a filesytem tree using rsync."""
        rsync(Path('/foo/bar'), '1.2.3.4')
        mock_check_call.assert_called_with(
            ['rsync', '-a', '/foo/bar', '1.2.3.4:/foo/bar'])

    @mock.patch('subprocess.check_call')
    def test_rsync_delete(self, mock_check_call):
        """If the delete flag is True, the --delete option is passed."""
        rsync(Path('/foo/bar'), '1.2.3.4', delete=True)
        mock_check_call.assert_called_with(
            ['rsync', '-a', '--delete', '/foo/bar', '1.2.3.4:/foo/bar'])
