"""Repository configuration functions."""

import getpass

from charmhelpers.core.templating import render

from archive_auth_mirror.utils import (
    get_paths,
    update_config,
)


def configure_reprepro(mirrors, sign_key_fingerprint, sign_key_passphrase):
    """Create reprepro configuration files.

    The provided mirrors is a sequence of mirror.Mirror named tuples.
    """
    paths = get_paths()
    # Explicitly pass owner and group for tests, otherwise root would be used.
    owner = group = getpass.getuser()
    # Render distributions file.
    target = str(paths['reprepro-conf'] / 'distributions')
    context = {
        'mirrors': mirrors,
        'sign_script': paths['bin'] / 'reprepro-sign-helper',
    }
    render(_DISTRIBUTIONS, target, context, owner=owner, group=group)
    # Render updates file.
    target = str(paths['reprepro-conf'] / 'updates')
    context = {'mirrors': mirrors}
    render(_UPDATES, target, context, owner=owner, group=group)
    # Update configuration.
    update_config(
        config_path=paths['config'],
        suites=[mirror.local_suite for mirror in mirrors],
        sign_key_id=sign_key_fingerprint)
    # Save the sign passphrase for the signing helper script.
    with paths['sign-passphrase'].open('w') as fh:
        fh.write(sign_key_passphrase)


def disable_mirroring(get_paths=get_paths):
    """Disable mirroring."""
    config = get_paths()['config']
    if config.exists():
        config.replace(config.with_suffix('.disabled'))


_DISTRIBUTIONS = 'reprepro-distributions.j2'
_UPDATES = 'reprepro-updates.j2'
