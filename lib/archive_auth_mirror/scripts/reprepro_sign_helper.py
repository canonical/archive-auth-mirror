"""Helper for reprepro to sign archive lists."""

import sys
import argparse
from pathlib import Path

from ..utils import get_config
from ..gpg import inline_sign, detach_sign
from ..script import setup_logger


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Wrapper for GPG signing for reprepro')
    parser.add_argument(
        'unsigned_file', help='The file to sign.')
    parser.add_argument(
        'inline_sign_file', help='Name of the inline-signed file')
    parser.add_argument(
        'detach_sign_file', help='Name of the detached signature file')
    return parser.parse_args(args=args)


def patch_release_file(path, packages_require_auth):
    """Insert some custom fields in the Release file."""
    patch_path = path.with_suffix(".patched")
    with path.open() as file:
        with patch_path.open("x") as outfile:
            for line in file:
                if line.startswith('Codename:'):
                    line = line.rstrip().split('-')[0] + '\n'
                elif packages_require_auth and line.startswith("MD5Sum:"):
                    outfile.write("Packages-Require-Authorization: yes\n")
                outfile.write(line)
    patch_path.rename(path)


def main():
    logger = setup_logger()
    config = get_config()
    if not config:
        logger.error('no config file found')
        sys.exit(1)
    sign_key = config['sign-key-id']

    args = parse_args()
    unsigned_file = Path(args.unsigned_file)
    patch_release_file(
        unsigned_file, config.get('packages-require-auth', False))
    if args.inline_sign_file:
        inline_sign(sign_key, unsigned_file, Path(args.inline_sign_file))
    if args.detach_sign_file:
        detach_sign(sign_key, unsigned_file, Path(args.detach_sign_file))
