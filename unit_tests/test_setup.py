from unittest import TestCase, mock
import os
from pathlib import Path

from testtools.matchers import (
    FileContains,
    DirContains,
    Contains,
)

from charmtest import CharmTest

from charms.archive_auth_mirror.setup import (
    get_virtualhost_name,
    get_virtualhost_config,
    install_resources,
    create_script_file,
    have_required_config,
)

from fakes import FakeHookEnv


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
             'auth_backends': [],
             'basic_auth_file': '/srv/archive-auth-mirror/basic-auth'},
            config)

    def test_virtualhost_config_auth_backends(self):
        """If backends are passed, they're included in the vhost config."""
        hookenv = FakeHookEnv()
        auth_backends = [('1.2.3.4', '8080'), ('5.6.7.8', '9090')]
        config = get_virtualhost_config(
            auth_backends=auth_backends, hookenv=hookenv)
        self.assertEqual(
            {'domain': '1.2.3.4',
             'document_root': '/srv/archive-auth-mirror/static',
             'auth_backends': auth_backends,
             'basic_auth_file': '/srv/archive-auth-mirror/basic-auth'},
            config)


class InstallResourcesTests(CharmTest):

    def setUp(self):
        super().setUp()
        self.root_dir = self.fakes.fs.root
        os.makedirs(self.root_dir.join('etc/cron.d'))

        patcher_chown = mock.patch('os.chown')
        patcher_chown.start()
        self.addCleanup(patcher_chown.stop)

        patcher_pwnam = mock.patch('pwd.getpwnam')
        mock_pwnam = patcher_pwnam.start()
        mock_pwnam.return_value.pw_uid = 0
        self.addCleanup(patcher_pwnam.stop)

        patcher_grnam = mock.patch('grp.getgrnam')
        mock_grnam = patcher_grnam.start()

        def getgrnam(group):
            gr_gid = 123 if group == 'www-data' else 0
            return mock.MagicMock(gr_gid=gr_gid)

        mock_grnam.side_effect = getgrnam
        self.addCleanup(patcher_grnam.stop)

        patcher_fchown = mock.patch('os.fchown')
        self.mock_fchown = patcher_fchown.start()
        self.addCleanup(patcher_fchown.stop)

    def test_tree(self):
        """The install_resources function creates the filesystem structure."""
        install_resources(root_dir=Path(self.root_dir.path))
        paths = ['basic-auth', 'bin', 'static', 'reprepro', 'sign-passphrase']
        self.assertThat(
            self.root_dir.join('srv/archive-auth-mirror'), DirContains(paths))

    def test_resources(self):
        """Resources from the charm are copied to the service tree."""
        install_resources(root_dir=Path(self.root_dir.path))
        self.assertThat(
            self.root_dir.join('srv/archive-auth-mirror/bin/mirror-archive'),
            FileContains(matcher=Contains("import mirror_archive")))
        self.assertThat(
            self.root_dir.join('srv/archive-auth-mirror/bin/manage-user'),
            FileContains(matcher=Contains("import manage_user")))
        sign_script_path = 'srv/archive-auth-mirror/bin/reprepro-sign-helper'
        self.assertThat(
            self.root_dir.join(sign_script_path),
            FileContains(matcher=Contains("import reprepro_sign_helper")))
        auth_file = self.root_dir.join('srv/archive-auth-mirror/basic-auth')
        self.assertEqual(0o100640, os.stat(auth_file).st_mode)

    def test_basic_auth_file_owner(self):
        """The basic-auth file is group-owned by www-data."""
        install_resources(root_dir=Path(self.root_dir.path))
        # the file ownership is changed to the gid for www-data
        self.mock_fchown.assert_any_call(mock.ANY, 0, 123)


class CreateScriptFileTest(CharmTest):

    def test_crate_script_file(self):
        """create_script_file renders a python script file."""
        bindir = Path(self.fakes.fs.root.path)
        create_script_file('foo', bindir)
        script = bindir / 'foo'
        content = script.read_text()

        shebang = '#!{}/.venv/bin/python3\n'.format(Path.cwd().parent)
        self.assertTrue(content.startswith(shebang))
        self.assertIn('from archive_auth_mirror.scripts import foo', content)
        self.assertIn('foo.main()', content)
        self.assertEqual(0o100755, script.stat().st_mode)


class HaveRequiredConfigsTest(TestCase):

    def test_all_options(self):
        """If all required options are set, the function returns True."""
        config = {
            'mirror-uri': 'http://example.com/ubuntu precise main',
            'mirror-archs': 'amd64 i386',
            'mirror-gpg-key': 'aabbcc',
            'sign-gpg-key': 'ddeeff',
            'repository-origin': 'Ubuntu'}
        self.assertTrue(have_required_config(config))

    def test_option_not_present(self):
        """If an option is not present, the function returns False."""
        # no mirror-gpg-key
        config = {
            'mirror-uri': 'http://example.com/ubuntu precise main',
            'mirror-archs': 'amd64 i386',
            'sign-gpg-key': 'ddeeff',
            'repository-origin': 'Ubuntu'}
        self.assertFalse(have_required_config(config))

    def test_option_none(self):
        """If an option has a None value, the function returns False."""
        config = {
            'mirror-uri': 'http://example.com/ubuntu precise main',
            'mirror-archs': None,
            'mirror-gpg-key': 'aabbcc',
            'sign-gpg-key': 'ddeeff',
            'repository-origin': 'Ubuntu'}
        self.assertFalse(have_required_config(config))

    def test_option_empty_string(self):
        """If an option is an empty string, the function returns False."""
        config = {
            'mirror-uri': 'http://example.com/ubuntu precise main',
            'mirror-archs': 'amd64 i386',
            'mirror-gpg-key': '',
            'sign-gpg-key': 'ddeeff',
            'repository-origin': 'Ubuntu'}
        self.assertFalse(have_required_config(config))
