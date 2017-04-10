from pathlib import Path

from fixtures import TestWithFixtures, TempDir

from archive_auth_mirror.utils import get_paths
from archive_auth_mirror.cron import install_crontab, remove_crontab


class InstallCrontabTest(TestWithFixtures):

    def test_install_crontab(self):
        """install_crontab creates a crontab file"""
        root_dir = Path(self.useFixture(TempDir()).path)
        (root_dir / 'etc/cron.d').mkdir(parents=True)
        paths = get_paths(root_dir=root_dir)
        install_crontab(paths=paths)

        with paths['cron'].open() as fh:
            content = fh.read()

        script = paths['bin'] / 'mirror-archive'
        self.assertIn(str(script), content)


class RemoveCrontabTest(TestWithFixtures):

    def setUp(self):
        super().setUp()
        self.root_dir = Path(self.useFixture(TempDir()).path)
        (self.root_dir / 'etc/cron.d').mkdir(parents=True)
        self.paths = get_paths(root_dir=self.root_dir)

    def test_remove_crontab(self):
        """remove_crontab removes the crontab file."""
        install_crontab(paths=self.paths)
        remove_crontab(paths=self.paths)
        self.assertFalse(self.paths['cron'].exists())

    def test_remove_crontab_not_existent(self):
        """If the crontab file doesn't exist, remove_crontab no-ops."""
        self.assertFalse(self.paths['cron'].exists())
        remove_crontab(paths=self.paths)
        self.assertFalse(self.paths['cron'].exists())
