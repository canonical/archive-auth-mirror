import textwrap
import unittest
from pathlib import Path

from charmtest import CharmTest

from charms.archive_auth_mirror.utils import get_paths
from charms.archive_auth_mirror.reprepro import (
    configure_reprepro,
    disable_mirroring,
    split_repository_uri,
)


class ConfigureRepreproTest(CharmTest):

    def test_configuration_files(self):
        """configure_reprepro writes rerepro config files."""
        paths = get_paths(root_dir=Path(self.fakes.fs.root.path))
        uri = 'https://user:pass@example.com/ubuntu xenial main universe'
        configure_reprepro(
            uri, 'i386 amd64', 'ABABABAB', 'CDCDCDCD', 'very secret',
            get_paths=lambda: paths)
        self.assertEqual(
            textwrap.dedent(
                '''\
                Codename: xenial
                Label: xenial archive
                Components: main universe
                Architectures: i386 amd64
                SignWith: ! {}/reprepro-sign-helper
                Update: update-repo
                '''.format(paths['bin'])),
            (paths['reprepro-conf'] / 'distributions').read_text())
        self.assertEqual(
            textwrap.dedent(
                '''\
                Name: update-repo
                Method: https://user:pass@example.com/ubuntu
                Suite: xenial
                Components: main universe
                Architectures: i386 amd64
                VerifyRelease: ABABABAB
                '''),
            (paths['reprepro-conf'] / 'updates').read_text())
        self.assertEqual(
            textwrap.dedent(
                '''\
                SUITE=xenial
                SIGN_KEY_ID=CDCDCDCD
                '''),
            paths['config'].read_text())


class DisableMirroringTest(CharmTest):

    def test_disable_mirroring(self):
        """disable_mirroring renames the script config file."""
        paths = get_paths(root_dir=Path(self.fakes.fs.root.path))
        uri = 'https://user:pass@example.com/ubuntu xenial main universe'
        configure_reprepro(
            uri, 'i386 amd64', 'ABABABAB', 'CDCDCDCD', 'very secret',
            get_paths=lambda: paths)

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
        """Disabling mirror when not configured is a no-op."""
        paths = get_paths(root_dir=Path(self.fakes.fs.root.path))
        config = paths['config']
        disable_mirroring(get_paths=lambda: paths)
        self.assertFalse(config.exists())
        self.assertFalse(config.with_suffix('.disabled').exists())

    def test_disable_twice(self):
        """disable_mirroring can be called multiple times."""
        paths = get_paths(root_dir=Path(self.fakes.fs.root.path))
        config = paths['config']
        disable_mirroring(get_paths=lambda: paths)
        disable_mirroring(get_paths=lambda: paths)
        self.assertFalse(config.exists())
        self.assertFalse(config.with_suffix('.disabled').exists())


class SplitRepositoryUriTest(unittest.TestCase):

    def test_uri(self):
        """split_repository_uri splits the repository URI into tokens."""
        tokens = split_repository_uri(
            'https://user:pass@example.com/ubuntu xenial main universe')
        self.assertEqual(
            {'url': 'https://user:pass@example.com/ubuntu',
             'suite': 'xenial',
             'components': 'main universe'},
            tokens)
