import shutil
from pathlib import Path

from charms.reactive import when_not, set_state

# The filesystem tree for the service is as follows:
#
#  /srv/ubuntu-esm
#  ├── bin
#  │   └── ubuntu-esm-mirror  -- the mirroring script
#  ├── reprepro
#  │   └── conf -- reprepro configuration files
#  └── static   -- the root of the virtualhost, contains the repository
#
BASE_DIR = Path('/srv/ubuntu-esm')
REPREPRO_CONF_DIR = BASE_DIR / 'reprepro/conf'
BIN_DIR = BASE_DIR / 'bin'
STATIC_DIR = BASE_DIR / 'static'


@when_not('ubuntu-esm.installed')
def install():
    _install_resources()
    set_state('ubuntu-esm.installed')


def _install_resources():
    '''Create tree structure and copy resources from the charm.'''
    for directory in BASE_DIR, BIN_DIR, REPREPRO_CONF_DIR, STATIC_DIR:
        directory.mkdir(parents=True, exist_ok=True)
    shutil.copy('resources/index.html', str(STATIC_DIR))
    shutil.copy('resources/ubuntu-esm-mirror', str(BIN_DIR))
