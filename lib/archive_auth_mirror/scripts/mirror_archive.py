"""Mirror and update a repository."""

import subprocess
import sys

from ..utils import get_paths
from ..reprepro import Reprepro
from ..rsync import rsync_multi
from ..script import (
    setup_logger,
    get_config,
)


def main():
    logger = setup_logger(echo=True)
    paths = get_paths()
    config = get_config(paths['config'])
    suite = config['suite']
    other_units = config['ssh-peers'].keys()
    # Using StrictHostKeyChecking=no isn't ideal, but we don't yet
    # popolate known_hosts with the right keys. But we trust the
    # network, and we don't push any sensitive data.
    rsh = 'ssh -o StrictHostKeyChecking=no -i {}'.format(paths['ssh-key'])

    logger.info('starting mirroring')

    reprepro = Reprepro(logger)
    try:
        logger.info('fetching new pool packages')
        reprepro.execute(
            '--show-percent', '--export=never', '--keepunreferencedfiles',
            'update', suite)

        logger.info('rsyncing new pool packages to peer units')
        rsync_multi(paths['static'] / 'ubuntu', other_units, logger, rsh=rsh)

        logger.info('generating new dists directory')
        reprepro.execute('export', suite)

        logger.info('rsyncing new dists directory to peer units')
        rsync_multi(
            paths['static'] / 'ubuntu' / 'dists', other_units, logger, rsh=rsh)

        logger.info('deleting old pool packages')
        reprepro.execute('deleteunreferenced')

        logger.info('deleting old pool packages on peer units')
        rsync_multi(
            paths['static'] / 'ubuntu', other_units, logger, rsh=rsh,
            delete=True)

        logger.info('rsyncing reprepro dir to peer units')
        # Push only the reprepro db and lists, not the conf dir. Each
        # unit should generate the conf dir themselves, so we don't push
        # it, since it contains the private signing key, which is
        # sensitive data.
        rsync_multi(
            paths['reprepro'] / 'db', other_units, logger, rsh=rsh,
            delete=True)
        rsync_multi(
            paths['reprepro'] / 'lists', other_units, logger, rsh=rsh,
            delete=True)

        logger.info('mirroring completed')
    except subprocess.CalledProcessError:
        logger.error('mirroring failed')
        sys.exit(1)
