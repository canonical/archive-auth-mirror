"""Mirror and update a repository."""

from ..utils import get_paths
from ..reprepro import reprepro
from ..script import (
    setup_logger,
    get_config,
)


def main():
    logger = setup_logger()
    paths = get_paths()
    suite = get_config(paths['config'])['suite']

    logger.info('starting mirroring')
    reprepro(
        '--show-percent', '--export=never', '--keepunreferencedfiles',
        'update', suite)
    reprepro('export', suite)
    reprepro('deleteunreferenced')
    logger.info('mirroring completed')
