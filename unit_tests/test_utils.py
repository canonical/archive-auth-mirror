from pathlib import Path

from unittest import TestCase

from archive_auth_mirror.utils import get_paths


class GetPathsTest(TestCase):

    def test_get_paths(self):
        """get_paths returns service paths."""
        paths = get_paths()
        self.assertEqual(
            {'base': Path('/srv/archive-auth-mirror'),
             'cron': Path('/etc/cron.d/archive-auth-mirror'),
             'bin': Path('/srv/archive-auth-mirror/bin'),
             'config': Path('/srv/archive-auth-mirror/config'),
             'static': Path('/srv/archive-auth-mirror/static'),
             'basic-auth': Path('/srv/archive-auth-mirror/basic-auth'),
             'sign-passphrase': Path(
                 '/srv/archive-auth-mirror/sign-passphrase'),
             'reprepro': Path('/srv/archive-auth-mirror/reprepro'),
             'reprepro-conf': Path('/srv/archive-auth-mirror/reprepro/conf'),
             'gnupghome': Path('/srv/archive-auth-mirror/reprepro/.gnupg')},
            paths)
