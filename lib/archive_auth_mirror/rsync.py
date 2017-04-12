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
    command = ['/usr/bin/rsync', '-a']
    if delete:
        command.append('--delete')
    command.extend([path, '{}:{}'.format(host, path)])
    subprocess.check_output(command)


def rsync_multi(path, hosts, logger, delete=False):
    """Copy a filesystem tree using rsync to multiple hosts.

    If a call to rsync to a host fails, the error is logged via the provided
    logger and the next host is attempted.

    """
    for host in hosts:
        try:
            rsync(path, host, delete=delete)
        except subprocess.CalledProcessError as error:
            logger.error(
                'rsync to {} failed: {}'.format(host, error.output))
