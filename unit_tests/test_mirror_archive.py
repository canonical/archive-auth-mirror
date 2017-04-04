from unittest import TestCase, mock

from archive_auth_mirror.scripts.mirror_archive import reprepro


class RepreproTest(TestCase):

    @mock.patch('subprocess.check_call')
    def test_reprepro(self, mock_check_call):
        """The reprepro function calls reprepro with the specified args."""
        reprepro('export', 'ubuntu')
        mock_check_call.assert_called_with(
            ['reprepro',
             '--basedir', '/srv/archive-auth-mirror/reprepro',
             '--confdir', '/srv/archive-auth-mirror/reprepro/conf',
             '--outdir', '/srv/archive-auth-mirror/static/ubuntu',
             '--gnupghome', '/srv/archive-auth-mirror/reprepro/.gnupg',
             'export', 'ubuntu'])
