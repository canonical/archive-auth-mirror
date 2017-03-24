import shutil
from pathlib import Path
import textwrap

from charms.reactive import (
    when_not,
    set_state,
)
from charms.reactive.decorators import hook
from charmhelpers.core import hookenv


BASE_DIR = Path('/srv/ubuntu-esm')
REPREPRO_DIR = BASE_DIR / 'repo'
STATIC_DIR = BASE_DIR / 'static'


@when_not('ubuntu-esm.installed')
def install():
    _install_resources()
    set_state('ubuntu-esm.installed')


@hook('static-website-relation-{joined,changed}')
def website_relation():
    config = _get_website_relation_config(domain=hookenv.unit_public_ip())
    hookenv.relation_set(hookenv.relation_id(), config)


def _install_resources():
    '''Create tree structure and copy resources from the charm.'''
    for directory in BASE_DIR, STATIC_DIR, REPREPRO_DIR:
        directory.mkdir(exist_ok=True)
    shutil.copy('resources/index.html', str(STATIC_DIR))


def _get_website_relation_config(domain=None):
    '''Return the configuration for the 'static-website' relation.'''
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
            document_root=STATIC_DIR))
    return {
        'domain': domain,
        'enabled': True,
        'site_config': vhost_config,
        'site_modules': ['autoindex'],
        'ports': '80'}
