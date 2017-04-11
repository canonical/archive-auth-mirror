import unittest
from pathlib import Path
import shutil
import stat
import tempfile

from archive_auth_mirror.ssh import (
    add_authorized_key,
    create_key,
)


class CreateKeyTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, str(self.tempdir))

    def test_create_key(self):
        """create_key() creates a secret and public key.

        The secret key can only be read by the owner.
        """
        ssh_key_path = self.tempdir / 'ssh-key'
        create_key(ssh_key_path)
        public_key_path = ssh_key_path.with_suffix('.pub')
        self.assertEqual(0o644, stat.S_IMODE(public_key_path.stat().st_mode))
        self.assertEqual(0o600, stat.S_IMODE(ssh_key_path.stat().st_mode))
        self.assertIn('BEGIN RSA PRIVATE KEY', ssh_key_path.read_text())


class AddAuthorizedKey(unittest.TestCase):

    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, str(self.tempdir))

    def test_add_authorized_key(self):
        """add_authorized_key() adds the given key."""
        authorized_keys_path = self.tempdir / 'authorized-keys'
        add_authorized_key('key 1', authorized_keys_path)
        self.assertEqual(
            ['key 1'], authorized_keys_path.read_text().splitlines())

    def test_add_authorized_key_whitespace(self):
        """Whitespace gets stripped before adding the key."""
        authorized_keys_path = self.tempdir / 'authorized-keys'
        add_authorized_key('\nkey 1\n', authorized_keys_path)
        self.assertEqual(
            ['key 1'], authorized_keys_path.read_text().splitlines())

    def test_add_authorized_key_multiple(self):
        """Existing keys are preserved."""
        authorized_keys_path = self.tempdir / 'authorized-keys'
        add_authorized_key('key 1', authorized_keys_path)
        add_authorized_key('key 2', authorized_keys_path)
        self.assertEqual(
            ['key 1', 'key 2'], authorized_keys_path.read_text().splitlines())

    def test_add_authorized_key_duplicate(self):
        """If the key already exists in the, it's not added again."""
        authorized_keys_path = self.tempdir / 'authorized-keys'
        add_authorized_key('key 1', authorized_keys_path)
        add_authorized_key('key 1', authorized_keys_path)
        self.assertEqual(
            ['key 1'], authorized_keys_path.read_text().splitlines())
