import os
import shutil
from pathlib import Path

from charmhelpers.core import hookenv, host

from archive_auth_mirror.utils import get_paths


REQUIRED_OPTIONS = frozenset(
    ['mirror-uri', 'mirror-archs', 'mirror-gpg-key', 'sign-gpg-key'])


SCRIPTS = ('mirror-archive', 'manage-user', 'reprepro-sign-helper')


def get_virtualhost_name(hookenv=hookenv):
    """Return the configured service URL or the unit address."""
    service_url = hookenv.config().get('service-url')
    return service_url or hookenv.unit_public_ip()


def get_virtualhost_config(hookenv=hookenv):
    """Return the configuration for the static virtuahost."""
    paths = get_paths()
    domain = get_virtualhost_name(hookenv=hookenv)
    return {
        'domain': domain,
        'document_root': str(paths['static']),
        'basic_auth_file': str(paths['basic-auth'])}


def install_resources(root_dir=None):
    """Create tree structure and copy resources from the charm."""
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

    # copy scripts
    for resource in SCRIPTS:
        resource_path = os.path.join('resources', resource)
        shutil.copy(resource_path, str(paths['bin']))
    # install crontab
    shutil.copy('resources/crontab', str(paths['cron']))
    # symlink the lib libary to make it available to scripts too
    (paths['bin'] / 'lib').symlink_to(Path.cwd() / 'lib')


def have_required_config(config):
    """Return whether all required config options are set."""
    return all(
        config.get(option) not in ('', None) for option in REQUIRED_OPTIONS)
