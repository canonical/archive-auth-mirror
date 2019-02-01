import tempfile
import textwrap
from unittest import mock
from pathlib import Path

import yaml

from charmtest import CharmTest

from archive_auth_mirror.utils import get_paths
from archive_auth_mirror.scripts.reprepro_sign_helper import patch_release_file
from archive_auth_mirror.mirror import Mirror
from charms.archive_auth_mirror.repository import (
    configure_reprepro,
    disable_mirroring,
)


def make_reprepro_files(root_dir, mirrors):
    """A tiny wrapper around configure_reprepro with testing paths."""
    paths = get_paths(root_dir=Path(root_dir))
    with mock.patch(
        'charms.archive_auth_mirror.repository.get_paths', return_value=paths
    ):
        configure_reprepro(mirrors, sign_key_fingerprint, sign_key_passphrase)
    return paths


class ConfigureRepreproTest(CharmTest):

    def test_configuration_files(self):
        """configure_reprepro writes rerepro config files."""
        paths = make_reprepro_files(self.fakes.fs.root.path, mirrors)
        self.assertEqual(
            textwrap.dedent(
                '''\
                Codename: xenial
                Suite: xenial
                Version: 18.10
                Label: Ubuntu
                Origin: Ubuntu
                Components: main universe
                Architectures: source i386 amd64
                SignWith: ! {bin}/reprepro-sign-helper
                Update: update-repo-xenial

                Codename: sid
                Suite: sid
                Label: Debian
                Origin: Debian
                Components: multiverse
                Architectures: source
                SignWith: ! {bin}/reprepro-sign-helper
                Update: update-repo-sid

                '''.format(**paths)),
            (paths['reprepro-conf'] / 'distributions').read_text())
        self.assertEqual(
            textwrap.dedent(
                '''\
                Name: update-repo-xenial
                Method: https://user:pass@example.com/ubuntu
                Suite: xenial
                Components: main universe
                Architectures: source i386 amd64
                VerifyRelease: finger

                Name: update-repo-sid
                Method: https://user:pass@1.2.3.4/debian
                Suite: sid
                Components: multiverse
                Architectures: source
                VerifyRelease: finger

                '''),
            (paths['reprepro-conf'] / 'updates').read_text())
        self.assertEqual(
            yaml.load(paths['config'].read_text()),
            {'sign-key-id': 'finger', 'suites': ['xenial', 'sid']})
        with paths['sign-passphrase'].open() as f:
            self.assertEqual(f.read(), 'secret')


class MiscRepositoryTests(CharmTest):

    def test_insert_packages_require_authorization(self):
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            f.write('Origin: anOrigin\nMD5Sum:\n')
        release_path = Path(f.name)
        self.addCleanup(release_path.unlink)
        patch_release_file(release_path)
        with release_path.open() as result_file:
            result = result_file.readlines()

        self.assertEqual("Origin: anOrigin\n", result[0])
        self.assertEqual("Packages-Require-Authorization: yes\n", result[1])
        self.assertEqual("MD5Sum:\n", result[2])
        self.assertEqual(3, len(result))


class DisableMirroringTest(CharmTest):

    def test_disable_mirroring(self):
        """disable_mirroring renames the script config file."""
        paths = make_reprepro_files(self.fakes.fs.root.path, mirrors)

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


mirrors = (
    Mirror(
        url='https://user:pass@example.com/ubuntu',
        suite='xenial',
        components='main universe',
        key='finger',
        archs='source i386 amd64',
        version='18.10',
        origin='Ubuntu',
    ),
    Mirror(
        url='https://user:pass@1.2.3.4/debian',
        suite='sid',
        components='multiverse',
        key='finger',
        archs='source',
        version='',
        origin='Debian',
    ),
)
sign_key_fingerprint, sign_key_passphrase = 'finger', 'secret'
