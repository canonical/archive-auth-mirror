import subprocess

from .utils import get_paths


def create_key(get_paths=get_paths):
    subprocess.check_call([
        'ssh-keygen', '-f', str(get_paths()['ssh-key']), '-t', 'rsa',
        '-N', ''])


def get_public_key(get_paths=get_paths):
    public_key_path = str(get_paths()['ssh-key']) + '.pub'
    with open(public_key_path, 'r') as public_key_file:
        return public_key_file.read()


def add_authorized_key(public_key, get_paths=get_paths):
    authorized_keys_path = get_paths()['authorized-keys']
    ssh_dir = authorized_keys_path.parent
    if not ssh_dir.exists():
        ssh_dir.mkdir(0o700)
    with authorized_keys_path.open('r') as authorized_keys_file:
        authorized_keys = authorized_keys_file.readlines()
    if public_key in authorized_keys:
        return
    with authorized_keys_path.open('a') as authorized_keys_file:
        authorized_keys_file.write(public_key)
