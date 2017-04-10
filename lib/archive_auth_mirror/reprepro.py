"""Wrappers around the rsync tool."""

import subprocess

from .utils import get_paths


def reprepro(*args):
    """Call reprepro with the specified args."""
    paths = get_paths()
    command = [
        'reprepro',
        '--basedir', str(paths['reprepro']),
        '--confdir', str(paths['reprepro-conf']),
        '--outdir', str(paths['static'] / 'ubuntu'),
        '--gnupghome', str(paths['gnupghome'])]
    command.extend(args)
    subprocess.check_call(command)
