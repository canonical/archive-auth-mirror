import os
from unittest import TestCase, mock
import textwrap

from fixtures import TestWithFixtures, TempDir

from charms.archive_auth_mirror.utils import get_paths
from charms.archive_auth_mirror.reprepro import (
    configure_reprepro,
    disable_mirroring,
    split_repository_uri,
)


class ConfigureRepreproTest(TestWithFixtures):

    def setUp(self):
        super().setUp()
        self.tempdir = self.useFixture(TempDir())

    @mock.patch('charmhelpers.core.hookenv.charm_dir')
    def test_configuration_files(self, mock_charm_dir):
        '''configure_reprepro writes rerepro config files.'''
        mock_charm_dir.return_value = os.getcwd()

        paths = get_paths(self.tempdir.path)
        uri = 'https://user:pass@example.com/ubuntu xenial main universe'
        configure_reprepro(
            uri, 'i386 amd64', 'ABABABAB', 'CDCDCDCD', get_paths=lambda: paths)
        self.assertEqual(
            textwrap.dedent(
                '''\
                Codename: xenial
                Label: xenial archive
                Components: main universe
                UDebComponents: main universe
                Architectures: i386 amd64
                SignWith: CDCDCDCD
                Update: update-repo
                '''),
            (paths['reprepro-conf'] / 'distributions').read_text())
        self.assertEqual(
            textwrap.dedent(
                '''\
                Name: update-repo
                Method: https://user:pass@example.com/ubuntu
                Suite: xenial
                Components: main universe
                UDebComponents: main universe
                Architectures: i386 amd64
                VerifyRelease: ABABABAB
                '''),
            (paths['reprepro-conf'] / 'updates').read_text())
        self.assertEqual(
            'SUITE=xenial\n', paths['config'].read_text())


class DisableMirroringTest(TestWithFixtures):

    def setUp(self):
        super().setUp()
        self.tempdir = self.useFixture(TempDir())

    @mock.patch('charmhelpers.core.hookenv.charm_dir')
    def test_disable_mirroring(self, mock_charm_dir):
        '''disable_mirroring renames the script config file.'''
        mock_charm_dir.return_value = os.getcwd()

        paths = get_paths(self.tempdir.path)
        uri = 'https://user:pass@example.com/ubuntu xenial main universe'
        configure_reprepro(
            uri, 'i386 amd64', 'ABABABAB', 'CDCDCDCD', get_paths=lambda: paths)

        config = paths['config']
        self.assertTrue(config.exists())
        orig_content = config.read_text()
        disable_mirroring(get_paths=lambda: paths)
        self.assertFalse(config.exists())
        # The file is moved to .disabled
        disabled_file = config.with_suffix('.disabled')
        self.assertTrue(disabled_file.exists())
        self.assertEqual(orig_content, disabled_file.read_text())

    def test_disable_not_enabled(self):
        '''Disabling mirror when not configured is a no-op.'''
        paths = get_paths(self.tempdir.path)
        config = paths['config']
        disable_mirroring(get_paths=lambda: paths)
        self.assertFalse(config.exists())
        self.assertFalse(config.with_suffix('.disabled').exists())

    def test_disable_twice_(self):
        '''disable_mirroring can be called multiple times.'''
        paths = get_paths(self.tempdir.path)
        config = paths['config']
        disable_mirroring(get_paths=lambda: paths)
        disable_mirroring(get_paths=lambda: paths)
        self.assertFalse(config.exists())
        self.assertFalse(config.with_suffix('.disabled').exists())


class SplitRepositoryUriTest(TestCase):

    def test_uri(self):
        '''split_repo_uri splits the repository URI into tokens.'''
        tokens = split_repository_uri(
            'https://user:pass@example.com/ubuntu xenial main universe')
        self.assertEqual(
            {'url': 'https://user:pass@example.com/ubuntu',
             'suite': 'xenial',
             'components': 'main universe'},
            tokens)
