"""Wrapper around the rsync tool."""

import subprocess


def rsync(path, host, delete=False):
    """Copy a filesytem tree using rsync.

    The path is synced at the same location on the remote host.

    path must be a pathlib.Path instance.

    If delete is specified, files not found in the source path are removed from
    the destination.

    """
    path = str(path.absolute())
    command = ['rsync', '-a']
    if delete:
        command.append('--delete')
    command.extend([path, '{}:{}'.format(host, path)])
    subprocess.check_call(command)
