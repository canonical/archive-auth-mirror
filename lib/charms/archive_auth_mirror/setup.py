"""Service installation and configuration functions."""

from pathlib import Path

from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render

from archive_auth_mirror.utils import get_paths


REQUIRED_OPTIONS = frozenset(
    ['mirror-uri', 'mirror-archs', 'mirror-gpg-key', 'sign-gpg-key',
     'repository-origin'])


SCRIPTS = ('mirror-archive', 'manage-user', 'reprepro-sign-helper')


def get_virtualhost_name(hookenv=hookenv):
    """Return the configured service URL or the unit address."""
    service_url = hookenv.config().get('service-url')
    return service_url or hookenv.unit_public_ip()


def get_virtualhost_config(auth_backends=None, hookenv=hookenv):
    """Return the configuration for the static virtuahost."""
    paths = get_paths()
    domain = get_virtualhost_name(hookenv=hookenv)
    return {
        'domain': domain,
        'document_root': str(paths['static']),
        'auth_backends': auth_backends or [],
        'basic_auth_file': str(paths['basic-auth'])}


def get_frontend_services_config(hookenv=hookenv):
    """Return the config for the website relation frontend service """
    port = hookenv.config()['port']
    server_name = '{}-{}'.format(
        hookenv.local_unit().replace('/', '-'), port)
    return [
        {'service_name': hookenv.service_name(),
         'service_host': '0.0.0.0',
         'service_port': port,
         'service_options': [
             'mode http', 'balance leastconn', 'cookie SRVNAME insert'],
         'servers': [
             [server_name, hookenv.unit_private_ip(), port,
              'maxconn 100 cookie S{i} check']]}]


def install_resources(root_dir=None):
    """Create tree structure and install resources from the charm."""
    paths = get_paths(root_dir=root_dir)
    for name in ('bin', 'reprepro-conf', 'static'):
        host.mkdir(str(paths[name]), perms=0o755)

    # the gpg directory should only be readable by root
    host.mkdir(str(paths['gnupghome']), perms=0o700)

    # create an empty basic-auth password file. It will be updated by a script
    # run as root, but it must be readable by the web server
    host.write_file(
        str(paths['basic-auth']), b'', group='www-data', perms=0o640)
    # create an empty sign passphrase file, only readable by root
    host.write_file(str(paths['sign-passphrase']), b'', perms=0o600)

    # install scripts
    for script in SCRIPTS:
        create_script_file(script, paths['bin'])
    # symlink the lib libary to make it available to scripts too
    (paths['bin'] / 'lib').symlink_to(Path.cwd() / 'lib')


def create_script_file(name, bindir):
    """Write a python script file from the template."""
    context = {
        'interpreter': Path.cwd().parent / '.venv/bin/python3',
        'script_module': name.replace('-', '_')}
    render('script.j2', str(bindir / name), context, perms=0o755)


def have_required_config(config):
    """Return whether all required config options are set."""
    return all(
        config.get(option) not in ('', None) for option in REQUIRED_OPTIONS)
