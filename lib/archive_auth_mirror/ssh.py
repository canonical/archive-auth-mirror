import subprocess


def create_key(path):
    subprocess.check_call([
        'ssh-keygen', '-f', str(path), '-t', 'rsa', '-N', ''])


def add_authorized_key(public_key, authorized_keys_path):
    ssh_dir = authorized_keys_path.parent
    if not ssh_dir.exists():
        ssh_dir.mkdir(0o700)
    with authorized_keys_path.open('r') as authorized_keys_file:
        authorized_keys = authorized_keys_file.readlines()
    if public_key in authorized_keys:
        return
    with authorized_keys_path.open('a') as authorized_keys_file:
        authorized_keys_file.write(public_key)
