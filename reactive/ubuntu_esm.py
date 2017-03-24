import shutil
from pathlib import Path
import textwrap

from charms.reactive import (
    when_not,
    set_state,
)
from charms.reactive.decorators import hook
from charmhelpers.core import hookenv


@when_not('ubuntu-esm.installed')
def install():
    _install_resources()
    set_state('ubuntu-esm.installed')


@hook('static-website-relation-{joined,changed}')
def website_relation():
    config = _get_website_relation_config(hookenv.unit_public_ip())
    hookenv.relation_set(hookenv.relation_id(), config)


def _get_paths(base_dir=None):
    '''Return path for the service tree.

    The filesystem tree for the service is as follows:

    /srv/ubuntu-esm
    ├── bin
    │   └── ubuntu-esm-mirror  -- the mirroring script
    ├── reprepro
    │   └── conf -- reprepro configuration files
    └── static   -- the root of the virtualhost, contains the repository
    '''
    if base_dir is None:
        base_dir = '/srv/ubuntu-esm'
    base_dir = Path(base_dir)
    return {
        'base': base_dir,
        'bin': base_dir / 'bin',
        'reprepro': base_dir / 'reprepro',
        'static': base_dir / 'static'}


def _install_resources(base_dir=None):
    '''Create tree structure and copy resources from the charm.'''
    paths = _get_paths(base_dir=base_dir)
    for directory in paths.values():
        directory.mkdir(parents=True, exist_ok=True)
    shutil.copy('resources/index.html', str(paths['static']))
    shutil.copy('resources/ubuntu-esm-mirror', str(paths['bin']))


def _get_website_relation_config(domain):
    '''Return the configuration for the 'static-website' relation.'''
    paths = _get_paths()
    vhost_config = textwrap.dedent(
        '''
        <VirtualHost {domain}:80>
          DocumentRoot "{document_root}"
          Options +Indexes

          <Location />
            Require all granted
            Options +Indexes
          </Location>
        </VirtualHost>
        '''.format(
            domain=domain,
            document_root=paths['static']))
    return {
        'domain': domain,
        'enabled': True,
        'site_config': vhost_config,
        'site_modules': ['autoindex'],
        'ports': '80'}
