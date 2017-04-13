import os
from pathlib import Path

from charmtest import CharmTest

from archive_auth_mirror.lock import lock, unlock, is_valid_lock, AlreadyLocked


class LockTest(CharmTest):

    def setUp(self):
        super().setUp()
        self.lockfile = Path(self.fakes.fs.root.path) / 'lock'

    def test_lock_not_locked(self):
        """lock creates the lockfile if it doesn't exist."""
        lock(self.lockfile)
        self.assertEqual(str(os.getpid()), self.lockfile.read_text())

    def test_lock_locked(self):
        """lock raises an error if a valid lockfile exists."""
        self.lockfile.write_text(str(os.getpid()))
        self.assertRaises(AlreadyLocked, lock, self.lockfile)

    def test_lock_invalid_lockfile(self):
        """lock replaces an invalid lockfile."""
        self.lockfile.write_text('foo')
        lock(self.lockfile)
        self.assertEqual(str(os.getpid()), self.lockfile.read_text())


class UnlockTest(CharmTest):

    def setUp(self):
        super().setUp()
        self.lockfile = Path(self.fakes.fs.root.path) / 'lock'

    def test_remove_lockfile(self):
        """unlock removes an existing lockfile."""
        self.lockfile.write_text('foo')
        unlock(self.lockfile)
        self.assertFalse(self.lockfile.exists())

    def test_no_lock_file(self):
        """unlock is a no-op if the lockfile doesn't exist ."""
        self.assertFalse(self.lockfile.exists())
        unlock(self.lockfile)
        self.assertFalse(self.lockfile.exists())


class IsValidLock(CharmTest):

    def setUp(self):
        super().setUp()
        self.lockfile = Path(self.fakes.fs.root.path) / 'lock'

    def test_no_lock(self):
        """is_valid_lock returns False if there's no lockfile."""
        self.assertFalse(is_valid_lock(self.lockfile))

    def test_lockfile_invalid_content(self):
        """is_valid_lock returns False if the lockfile is invalid."""
        self.lockfile.write_text('foo')
        self.assertFalse(is_valid_lock(self.lockfile))

    def test_lockfile_unknown_process(self):
        """is_valid_lock returns False if the PID doesn't exist."""
        self.lockfile.write_text('-123')
        self.assertFalse(is_valid_lock(self.lockfile))

    def test_lockfile_process_exists(self):
        """is_valid_lock returns False if the PID doesn't exist."""
        self.lockfile.write_text(str(os.getpid()))
        self.assertTrue(is_valid_lock(self.lockfile))
