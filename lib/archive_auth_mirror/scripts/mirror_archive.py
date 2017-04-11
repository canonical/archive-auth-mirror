"""Mirror and update a repository."""

import subprocess
import sys

from ..utils import get_paths
from ..reprepro import Reprepro
from ..script import (
    setup_logger,
    get_config,
)


def main():
    logger = setup_logger(echo=True)
    paths = get_paths()
    suite = get_config(paths['config'])['suite']

    logger.info('starting mirroring')

    reprepro = Reprepro(logger)
    try:
        reprepro.execute(
            '--show-percent', '--export=never', '--keepunreferencedfiles',
            'update', suite)
        reprepro.execute('export', suite)
        reprepro.execute('deleteunreferenced')
        logger.info('mirroring completed')
    except subprocess.CalledProcessError:
        logger.error('mirroring failed')
        sys.exit(1)
