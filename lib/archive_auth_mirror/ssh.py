"""Helper functions to deal with ssh."""

import subprocess


def create_key(path):
    """Use ssh-keygen to create a new ssh key."""
    subprocess.check_call([
        'ssh-keygen', '-q', '-f', str(path), '-t', 'rsa', '-N', ''])


def add_authorized_key(public_key, authorized_keys_path):
    """Add the public key to the specified authorized_keys file."""
    ssh_dir = authorized_keys_path.parent
    if not ssh_dir.exists():
        ssh_dir.mkdir(0o700)
    if authorized_keys_path.exists():
        authorized_keys = authorized_keys_path.read_text().splitlines()
    else:
        authorized_keys = []
    public_key = public_key.strip()
    if public_key in authorized_keys:
        return
    with authorized_keys_path.open('a') as authorized_keys_file:
        authorized_keys_file.write(public_key + '\n')
