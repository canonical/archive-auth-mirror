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
                Codename: xenial-updates
                Suite: xenial
                Version: 18.10
                Label: Ubuntu
                Origin: Ubuntu
                Components: main universe
                Architectures: source i386 amd64
                SignWith: ! {bin}/reprepro-sign-helper
                Update: update-repo-xenial-updates

                Codename: sid-security
                Suite: sid
                Label: Debian
                Origin: Debian
                Components: multiverse
                Architectures: source
                SignWith: ! {bin}/reprepro-sign-helper
                Update: update-repo-sid-security

                '''.format(**paths)),
            (paths['reprepro-conf'] / 'distributions').read_text())
        self.assertEqual(
            textwrap.dedent(
                '''\
                Name: update-repo-xenial-updates
                Method: https://user:pass@example.com/ubuntu
                Suite: xenial
                Components: main universe
                Architectures: source i386 amd64
                VerifyRelease: finger

                Name: update-repo-sid-security
                Method: https://user:pass@1.2.3.4/debian
                Suite: sid
                Components: multiverse
                Architectures: source
                VerifyRelease: finger

                '''),
            (paths['reprepro-conf'] / 'updates').read_text())
        self.assertEqual(
            yaml.load(paths['config'].read_text()), {
                'sign-key-id': 'finger',
                'pockets': ['xenial-updates', 'sid-security'],
            })
        with paths['sign-passphrase'].open() as f:
            self.assertEqual(f.read(), 'secret')


class PatchReleaseFileTest(CharmTest):

    def make_release_file(self, codename):
        """Create a release file for testing. Return its path."""
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            f.write('Codename: {}\n'.format(codename))
            f.write('Origin: anOrigin\n')
            f.write('MD5Sum: aSum\n')
        path = Path(f.name)
        self.addCleanup(path.unlink)
        return path

    def test_with_authorization(self):
        release_path = self.make_release_file('xenial')
        packages_require_auth = True
        patch_release_file(release_path, packages_require_auth)
        with release_path.open() as f:
            content = f.read()
        self.assertEqual(
            content,
            'Codename: xenial\n'
            'Origin: anOrigin\n'
            'Packages-Require-Authorization: yes\n'
            'MD5Sum: aSum\n'
        )

    def test_without_authorization(self):
        release_path = self.make_release_file('trusty')
        packages_require_auth = False
        patch_release_file(release_path, packages_require_auth)
        with release_path.open() as f:
            content = f.read()
        self.assertEqual(
            content,
            'Codename: trusty\n'
            'Origin: anOrigin\n'
            'MD5Sum: aSum\n'
        )

    def test_with_two_words_pocket(self):
        release_path = self.make_release_file('xenial-updates')
        packages_require_auth = True
        patch_release_file(release_path, packages_require_auth)
        with release_path.open() as f:
            content = f.read()
        self.assertEqual(
            content,
            'Codename: xenial\n'
            'Origin: anOrigin\n'
            'Packages-Require-Authorization: yes\n'
            'MD5Sum: aSum\n'
        )

    def test_with_three_words_pocket(self):
        release_path = self.make_release_file('bionic-foo-bar')
        packages_require_auth = False
        patch_release_file(release_path, packages_require_auth)
        with release_path.open() as f:
            content = f.read()
        self.assertEqual(
            content,
            'Codename: bionic\n'
            'Origin: anOrigin\n'
            'MD5Sum: aSum\n'
        )


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
        pocket='xenial-updates',
    ),
    Mirror(
        url='https://user:pass@1.2.3.4/debian',
        suite='sid',
        components='multiverse',
        key='finger',
        archs='source',
        version='',
        origin='Debian',
        pocket='sid-security',
    ),
)
sign_key_fingerprint, sign_key_passphrase = 'finger', 'secret'
