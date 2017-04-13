"""Locking using a lock file."""

import fcntl


class AlreadyLocked(Exception):
    """A lock is already present."""


class LockFile:
    """A file used for locking."""

    _fh = None

    def __init__(self, path):
        self.path = path

    def lock(self):
        """Lock the file."""
        self.path.touch()
        self._fh = self.path.open('w')
        try:
            fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            self._close()
            raise AlreadyLocked()

    def release(self):
        """Release the lock on the file."""
        if self._fh is not None:
            fcntl.flock(self._fh, fcntl.LOCK_UN)
            self._close()

    def _close(self):
        self._fh.close()
        self._fh = None
