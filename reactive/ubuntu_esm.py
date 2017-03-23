import shutil
from pathlib import Path

from charms.reactive import when_not, set_state

BASE_DIR = Path('/srv/ubuntu-esm')
REPREPRO_DIR = BASE_DIR / 'repo'
STATIC_DIR = BASE_DIR / 'static'


@when_not('ubuntu-esm.installed')
def install():
    _install_resources()
    set_state('ubuntu-esm.installed')


def _install_resources():
    '''Create tree structure and copy resources from the charm.'''
    for directory in BASE_DIR, STATIC_DIR, REPREPRO_DIR:
        directory.mkdir(exist_ok=True)
    shutil.copy('resources/index.html', str(STATIC_DIR))
