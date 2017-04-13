"""Locking using a lock file."""

import os


class AlreadyLocked(Exception):
    """A lock is already present."""


def lock(lockfile):
    """Create a lockfile."""
    if is_valid_lock(lockfile):
        raise AlreadyLocked(lockfile)

    lockfile.write_text(str(os.getpid()))


def unlock(lockfile):
    """Remove an existing lock."""
    if lockfile.exists():
        lockfile.unlink()


def is_valid_lock(lockfile):
    """Return whether the lockfile exists and points to an existing process."""
    if not lockfile.exists():
        return False

    try:
        pid = int(lockfile.read_text())
    except ValueError:
        return False

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False

    return True
