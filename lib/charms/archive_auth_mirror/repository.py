"""Repository configuration functions."""

import getpass

from charmhelpers.core.templating import render

from archive_auth_mirror.utils import get_paths, update_config


def configure_reprepro(mirror_uri, mirror_archs, mirror_key_fingerprint,
                       sign_key_fingerprint, sign_key_passphrase, origin,
                       get_paths=get_paths):
    """Create reprepro configuration files."""
    paths = get_paths()
    context = split_repository_uri(mirror_uri)
    context.update(
        {'origin': origin,
         'archs': mirror_archs,
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
        config_path=paths['config'], suite=context['suite'],
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
