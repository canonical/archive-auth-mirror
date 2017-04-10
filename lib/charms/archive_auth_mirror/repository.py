import getpass

import yaml

from charmhelpers.core.templating import render

from archive_auth_mirror.utils import get_paths
from archive_auth_mirror.script import get_config


def configure_reprepro(mirror_uri, mirror_archs, mirror_key_fingerprint,
                       sign_key_fingerprint, sign_key_passphrase,
                       get_paths=get_paths):
    """Create reprepro configuration files."""
    paths = get_paths()
    context = split_repository_uri(mirror_uri)
    context.update(
        {'archs': mirror_archs,
         'mirror_key': mirror_key_fingerprint,
         'sign_key': sign_key_fingerprint,
         'sign_script': paths['bin'] / 'reprepro-sign-helper'})

    # explicitly pass owner and group for tests, otherwise root would be used
    owner = group = getpass.getuser()
    render(
        'reprepro-distributions.j2',
        str(paths['reprepro-conf'] / 'distributions'), context, owner=owner,
        group=group)
    render(
        'reprepro-updates.j2', str(paths['reprepro-conf'] / 'updates'),
        context, owner=owner, group=group)
    update_config(
        get_paths=get_paths, suite=context['suite'],
        sign_key_id=context['sign_key'])
    # save the sign passphrase for the signing helper script
    with paths['sign-passphrase'].open('w') as fh:
        fh.write(sign_key_passphrase)


def disable_mirroring(get_paths=get_paths):
    """Disable mirroring."""
    config = get_paths()['config']
    if config.exists():
        config.replace(config.with_suffix('.disabled'))


def split_repository_uri(uri):
    """Split the repository URI into components."""
    parts = ('url', 'suite', 'components')
    return dict(zip(parts, uri.split(' ', maxsplit=2)))


def update_config(get_paths=get_paths, suite=None, sign_key_id=None,
                  new_ssh_peers=None):
    paths = get_paths()
    config_path = paths['config']
    config = get_config(config_path)
    if suite is not None:
        config['suite'] = suite
    if sign_key_id is not None:
        config['sign-key-id'] = sign_key_id
    if new_ssh_peers is not None:
        ssh_peers = config.get('ssh-peers', {})
        ssh_peers.update(new_ssh_peers)
        config['ssh-peers'] = ssh_peers
    with config_path.open('w') as config_file:
        yaml.dump(config, config_file)
