from unittest import TestCase, mock
import os
from pathlib import Path

from fixtures import TempDir

from testtools.matchers import (
    FileContains,
    DirContains,
    Contains,
)

from charmtest import CharmTest

from charms.archive_auth_mirror.utils import (
    get_paths,
    get_virtualhost_name,
    get_virtualhost_config,
    install_resources,
)

from fakes import FakeHookEnv


class GetPathsTest(TestCase):

    def test_get_paths(self):
        """get_paths returns service paths."""
        paths = get_paths()
        self.assertEqual(
            {'base': Path('/srv/archive-auth-mirror'),
             'bin': Path('/srv/archive-auth-mirror/bin'),
             'config': Path('/srv/archive-auth-mirror/config'),
             'reprepro': Path('/srv/archive-auth-mirror/reprepro'),
             'reprepro-conf': Path('/srv/archive-auth-mirror/reprepro/conf'),
             'static': Path('/srv/archive-auth-mirror/static'),
             'gnupghome': Path('/srv/archive-auth-mirror/reprepro/.gnupg'),
             'basic-auth': Path('/srv/archive-auth-mirror/basic-auth')},
            paths)


class GetVirtualhostNameTest(TestCase):

    def test_get_no_config(self):
        """If the 'service-url' config is not set, the unit IP is returned."""
        hookenv = FakeHookEnv()
        self.assertEqual('1.2.3.4', get_virtualhost_name(hookenv=hookenv))

    def test_get_with_config(self):
        """If the 'service-url' config is set, it's used as virtualhost."""
        hookenv = FakeHookEnv(config={'service-url': 'example.com'})
        self.assertEqual('example.com', get_virtualhost_name(hookenv=hookenv))


class GetVirtualhostConfigTest(CharmTest):

    def test_virtualhost_config(self):
        """get_virtualhost_config returns the config for the virtualhost."""
        hookenv = FakeHookEnv()
        config = get_virtualhost_config(hookenv=hookenv)
        self.assertEqual(
            {'domain': '1.2.3.4',
             'document_root': '/srv/archive-auth-mirror/static',
             'basic_auth_file': '/srv/archive-auth-mirror/basic-auth'},
            config)


class InstallResourcesTests(CharmTest):

    def setUp(self):
        super().setUp()
        self.base_dir = self.useFixture(TempDir())
        self.cron_dir = self.useFixture(TempDir())

        patcher_chown = mock.patch('os.chown')
        patcher_chown.start()
        self.addCleanup(patcher_chown.stop)

        patcher_grnam = mock.patch('grp.getgrnam')
        mock_grnam = patcher_grnam.start()
        mock_grnam.return_value = mock.MagicMock(gr_gid=123)
        self.addCleanup(patcher_grnam.stop)

        patcher_fchown = mock.patch('os.fchown')
        self.mock_fchown = patcher_fchown.start()
        self.addCleanup(patcher_fchown.stop)

    def test_tree(self):
        """The install_resources function creates the filesystem structure."""
        install_resources(
            base_dir=self.base_dir.path, cron_dir=Path(self.cron_dir.path))
        self.assertThat(
            self.base_dir.path,
            DirContains(['basic-auth', 'bin', 'static', 'reprepro']))

    def test_resources(self):
        """Resources from the charm are copied to the service tree."""
        install_resources(
            base_dir=self.base_dir.path, cron_dir=Path(self.cron_dir.path))
        self.assertThat(
            self.base_dir.join('bin/mirror-archive'),
            FileContains(matcher=Contains("reprepro")))
        self.assertThat(
            self.base_dir.join('bin/manage-user'),
            FileContains(matcher=Contains("htpasswd")))
        script_path = '/srv/archive-auth-mirror/bin/mirror-archive'
        self.assertThat(
            self.cron_dir.join('archive-auth-mirror'),
            FileContains(matcher=Contains(script_path)))
        self.assertEqual(
            0o100640, os.stat(self.base_dir.join('basic-auth')).st_mode)

    def test_basic_auth_file_owner(self):
        """The basic-auth file is group-owned by www-data."""
        install_resources(
            base_dir=self.base_dir.path, cron_dir=Path(self.cron_dir.path))
        # the file ownership is changed to the gid for www-data
        self.mock_fchown.assert_called_with(mock.ANY, 0, 123)
