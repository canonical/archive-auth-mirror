from pathlib import Path
import textwrap
import shutil

from charmhelpers.core import hookenv


def get_paths(base_dir=None):
    """Return path for the service tree.

    The filesystem tree for the service is as follows:

    /srv/archive-auth-mirror
    ├── bin
    │   └── mirror-archive  -- the mirroring script
    ├── config  -- the script configuration file
    ├── reprepro
    │   └── conf  -- reprepro configuration files
    │       └── .gnupg  -- GPG config for reprepro
    └── static  -- the root of the virtualhost, contains the repository
    """
    if base_dir is None:
        base_dir = '/srv/archive-auth-mirror'
    base_dir = Path(base_dir)
    reprepro_dir = base_dir / 'reprepro'
    return {
        'base': base_dir,
        'bin': base_dir / 'bin',
        'config': base_dir / 'config',
        'reprepro': reprepro_dir,
        'reprepro-conf': reprepro_dir / 'conf',
        'static': base_dir / 'static',
        'gnupghome': reprepro_dir / '.gnupg'}


def get_virtualhost_name(hookenv=hookenv):
    """Return the configured service URL or the unit address."""
    service_url = hookenv.config().get('service-url')
    return service_url or hookenv.unit_public_ip()


def configure_website_relation():
    """Configure the 'static-website' relation."""
    domain = get_virtualhost_name()
    config = get_website_relation_config(domain)
    for relation_id in hookenv.relation_ids('static-website'):
        hookenv.relation_set(relation_id, config)


def get_website_relation_config(domain):
    """Return the configuration for the 'static-website' relation."""
    port = 80
    paths = get_paths()
    vhost_config = textwrap.dedent(
        '''
        <VirtualHost {domain}:{port}>
          DocumentRoot "{document_root}"

          <Location />
            Require all granted
            Options +Indexes
          </Location>
        </VirtualHost>
        '''.format(
            domain=domain, port=port,
            document_root=paths['static']))
    return {
        'domain': domain,
        'enabled': True,
        'site_config': vhost_config,
        'site_modules': ['autoindex'],
        'ports': [port]}


def install_resources(base_dir=None):
    """Create tree structure and copy resources from the charm."""
    paths = get_paths(base_dir=base_dir)
    for name in ('bin', 'reprepro-conf', 'static', 'gnupghome'):
        paths[name].mkdir(parents=True, exist_ok=True)
    shutil.copy('resources/mirror-archive', str(paths['bin']))
