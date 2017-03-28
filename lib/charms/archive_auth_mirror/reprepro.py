import getpass

from charmhelpers.core.templating import render

from .utils import get_paths


def configure_reprepro(mirror_uri, mirror_archs, mirror_key_fingerprint,
                       sign_key_fingerprint, get_paths=get_paths):
    '''Create reprepro configuration files.'''
    paths = get_paths()
    context = split_repository_uri(mirror_uri)
    context.update(
        {'archs': mirror_archs,
         'mirror_key': mirror_key_fingerprint,
         'sign_key': sign_key_fingerprint})
    # explicitly pass owner and group for tests, otherwise root would be used
    owner = group = getpass.getuser()
    render(
        'reprepro-distributions.j2',
        str(paths['reprepro-conf'] / 'distributions'), context, owner=owner,
        group=group)
    render(
        'reprepro-updates.j2', str(paths['reprepro-conf'] / 'updates'),
        context, owner=owner, group=group)
    render(
        'config.j2', str(paths['config']), context, owner=owner, group=group)


def disable_mirroring(get_paths=get_paths):
    '''Disable mirroring.'''
    config = get_paths()['config']
    if config.exists():
        config.replace(config.with_suffix('.disabled'))


def split_repository_uri(uri):
    '''Split the repository URI into components.'''
    parts = ('url', 'suite', 'components')
    return dict(zip(parts, uri.split(' ', maxsplit=2)))
