"""Service installation and configuration functions."""

from pathlib import Path

from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render

from archive_auth_mirror.utils import get_paths


REQUIRED_OPTIONS = frozenset(['mirrors', 'repository-origin', 'sign-gpg-key'])
SCRIPTS = ('mirror-archive', 'manage-user', 'reprepro-sign-helper')


def get_virtualhost_name(hookenv=hookenv):
    """Return the configured service URL or the unit address."""
    service_url = hookenv.config().get('service-url')
    return service_url or hookenv.unit_public_ip()


def get_virtualhost_config(
        auth_backends, auth_cache_enabled, auth_cache_duration,
        auth_cache_inactivity, hookenv=hookenv):
    """Return the configuration for the static virtuahost."""
    paths = get_paths()
    domain = get_virtualhost_name(hookenv=hookenv)
    return {
        'domain': domain,
        'document_root': str(paths['static']),
        'auth_backends': auth_backends or [],
        'auth_cache_enabled': auth_cache_enabled,
        'auth_cache_duration': auth_cache_duration,
        'auth_cache_inactivity': auth_cache_inactivity,
        'basic_auth_file': str(paths['basic-auth'])}


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


def missing_options(config):
    """Return a list of missing required option names if any.

    Return an empty list otherwise.
    """
    return [opt for opt in REQUIRED_OPTIONS if config.get(opt) in ('', None)]
