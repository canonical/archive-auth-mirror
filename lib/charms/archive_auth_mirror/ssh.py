import subprocess

from .utils import get_paths


def create_key(get_paths=get_paths):
    subprocess.check_call([
        'ssh-keygen', '-f', str(get_paths()['ssh-key']), '-t', 'rsa',
        '-N', ''])
