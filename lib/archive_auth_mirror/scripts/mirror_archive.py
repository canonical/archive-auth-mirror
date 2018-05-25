"""Mirror and update a repository."""

import functools
import subprocess
import sys

from ..utils import get_paths, get_config
from ..lock import LockFile, AlreadyLocked
from ..reprepro import Reprepro
from ..rsync import rsync_multi
from ..script import setup_logger


def main():
    logger = setup_logger(echo=True)
    paths = get_paths()
    config = get_config()
    suites = config['suites']
    other_units = config.get('ssh-peers', {}).keys()
    # Using StrictHostKeyChecking=no isn't ideal, but we don't yet
    # popolate known_hosts with the right keys. But we trust the
    # network, and we don't push any sensitive data.
    rsh = 'ssh -o StrictHostKeyChecking=no -i {}'.format(paths['ssh-key'])
    remote_sync = functools.partial(rsync_multi, other_units, rsh=rsh)
    lockfile = LockFile(paths['lockfile'])

    try:
        lockfile.lock()
    except AlreadyLocked:
        logger.error('another process is already running, exiting')
        sys.exit(1)

    logger.info('starting mirroring')

    reprepro = Reprepro(logger)
    try:
        logger.info('fetching new pool packages')
        reprepro.execute(
            '--show-percent', '--export=never', '--keepunreferencedfiles',
            'update', *suites)

        logger.info('rsyncing new pool packages to peer units')
        remote_sync(paths['static'] / 'ubuntu', logger)

        logger.info('generating new dists directory')
        reprepro.execute('export', *suites)

        logger.info('rsyncing new dists directory to peer units')
        remote_sync(paths['static'] / 'ubuntu' / 'dists', logger)

        logger.info('deleting old pool packages')
        reprepro.execute('deleteunreferenced')

        logger.info('deleting old pool packages on peer units')
        remote_sync(paths['static'] / 'ubuntu', logger, delete=True)

        logger.info('rsyncing reprepro dir to peer units')
        # Push only the reprepro db and lists, not the conf dir. Each
        # unit should generate the conf dir themselves, so we don't push
        # it, since it contains the private signing key, which is
        # sensitive data.
        remote_sync(paths['reprepro'] / 'db', logger, delete=True)
        remote_sync(paths['reprepro'] / 'lists', logger, delete=True)

        logger.info('mirroring completed')
    except subprocess.CalledProcessError:
        logger.error('mirroring failed')
        sys.exit(1)
    finally:
        lockfile.release()
