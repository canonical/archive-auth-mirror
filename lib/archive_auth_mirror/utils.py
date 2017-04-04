from pathlib import Path


def get_paths(root_dir=None):
    """Return path for the service tree.

    The filesystem tree for the service is as follows:

    /srv/archive-auth-mirror
    ├── basic-auth -- the file containing BasicAuth username/passwords
    ├── bin
    │   └── mirror-archive  -- the mirroring script
    ├── config.yaml  -- the script configuration file
    ├── reprepro
    │   └── conf  -- reprepro configuration files
    │       └── .gnupg  -- GPG config for reprepro
    ├── sign-passphrase  -- contains the passphrase for the GPG sign key
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
        'reprepro': reprepro_dir,
        'reprepro-conf': reprepro_dir / 'conf',
        'gnupghome': reprepro_dir / '.gnupg'}
