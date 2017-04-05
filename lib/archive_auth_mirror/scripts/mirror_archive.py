import subprocess

from ..utils import get_paths
from ..script import (
    setup_logger,
    get_config,
)


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


def main():
    logger = setup_logger()
    paths = get_paths()
    config = get_config(paths['config'])

    logger.info('starting mirroring')
    reprepro('--show-percent', 'update', config['suite'])
    reprepro('deleteunreferenced')
    logger.info('mirroring completed')
