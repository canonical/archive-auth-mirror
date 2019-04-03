"""Miscellaneous helper functions."""

from pathlib import Path

import yaml


def get_paths(root_dir=None):
    """Return path for the service tree.

    The filesystem tree for the service is as follows:

    /srv/archive-auth-mirror
    ├── basic-auth -- the file containing BasicAuth username/passwords
    ├── bin
    │   └── mirror-archive  -- the mirroring script
    ├── config.yaml  -- the script configuration file
    ├── mirror-archive.lock  -- lockfile for the mirror-archive script
    ├── reprepro
    │   └── conf  -- reprepro configuration files
    │       └── .gnupg  -- GPG config for reprepro
    ├── sign-passphrase  -- contains the passphrase for the GPG sign key
    ├── ssh-key  -- the ssh key used by rsync
    └── static  -- the root of the virtualhost, contains the repository
    """
    if root_dir is None:
        root_dir = Path('/')
    base_dir = root_dir / 'srv/archive-auth-mirror'
    reprepro_dir = base_dir / 'reprepro'
    return {
        'base': base_dir,
        'cron': root_dir / 'etc/cron.d/archive-auth-mirror',
        'bin': base_dir / 'bin',
        'config': base_dir / 'config.yaml',
        'static': base_dir / 'static',
        'basic-auth': base_dir / 'basic-auth',
        'sign-passphrase': base_dir / 'sign-passphrase',
        'ssh-key': base_dir / 'ssh-key',
        'authorized-keys': root_dir / 'root' / '.ssh' / 'authorized_keys',
        'lockfile': base_dir / 'mirror-archive.lock',
        'reprepro': reprepro_dir,
        'reprepro-conf': reprepro_dir / 'conf',
        'gnupghome': reprepro_dir / '.gnupg'}


def get_config(config_path=None):
    """Return a dict with the service configuration."""
    if config_path is None:
        config_path = get_paths()['config']
    if not config_path.exists():
        return {}
    with config_path.open() as fh:
        return yaml.load(fh)


def update_config(
        config_path=None, suites=(), sign_key_id=None, new_ssh_peers=None,
        packages_require_auth=None):
    """Update the config with the given parameters."""
    config = get_config(config_path=config_path)
    if suites:
        config['suites'] = suites
    if sign_key_id is not None:
        config['sign-key-id'] = sign_key_id
    if new_ssh_peers is not None:
        ssh_peers = config.get('ssh-peers', {})
        ssh_peers.update(new_ssh_peers)
        config['ssh-peers'] = ssh_peers
    if packages_require_auth is not None:
        config['packages-require-auth'] = packages_require_auth
    with config_path.open('w') as config_file:
        yaml.dump(config, config_file)
