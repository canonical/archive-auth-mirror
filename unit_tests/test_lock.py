from pathlib import Path

from charmtest import CharmTest

from archive_auth_mirror.lock import LockFile, AlreadyLocked


class LockFileTest(CharmTest):

    def setUp(self):
        super().setUp()
        self.file_path = Path(self.fakes.fs.root.path) / 'lock'
        self.lockfile = LockFile(self.file_path)
        self.addCleanup(self.lockfile.release)

    def test_lock_not_locked(self):
        """LockFile.lock creates the lockfile if it doesn't exist."""
        self.lockfile.lock()
        self.assertTrue(self.file_path.exists())

    def test_lock_locked(self):
        """If the file is already locked, and erorr is raised."""
        self.lockfile.lock()
        # try to lock with another instance
        other_lockfile = LockFile(self.file_path)
        self.addCleanup(other_lockfile.release)
        self.assertRaises(AlreadyLocked, other_lockfile.lock)

    def test_release(self):
        """Lockfile.release unlocks the file."""
        self.lockfile.lock()
        # try to lock with another instance
        other_lockfile = LockFile(self.file_path)
        self.addCleanup(other_lockfile.release)
        self.lockfile.release()
        # it's possible to lock the file with the other LockFile
        other_lockfile.lock()
        self.assertTrue(self.file_path.exists())
