import os
import shutil

from charms.reactive import when_not, set_state

BASE_DIR = '/srv/ubuntu-esm'
STATIC_DIR = BASE_DIR + '/static'


@when_not('ubuntu-esm.installed')
def install_ubuntu_esm():
    _ensure_tree()
    set_state('ubuntu-esm.installed')


def _ensure_tree():
    '''Ensure the tree structure on the filesystem is set up.'''
    if not os.path.isdir(STATIC_DIR):
        os.makedirs(STATIC_DIR)
    shutil.copy('resources/index.html', STATIC_DIR)
