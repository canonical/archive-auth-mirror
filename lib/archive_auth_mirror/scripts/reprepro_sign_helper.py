"""Helper for reprepro to sign archive lists."""

import sys
import argparse
from pathlib import Path

from ..utils import get_paths
from ..gpg import inline_sign, detach_sign
from ..script import setup_logger, get_config


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


def main():
    logger = setup_logger()
    paths = get_paths()
    config = get_config(paths['config'])
    if not config:
        logger.error('no config file found')
        sys.exit(1)
    sign_key = config['sign-key-id']

    args = parse_args()
    unsigned_file = Path(args.unsigned_file)
    if args.inline_sign_file:
        inline_sign(sign_key, unsigned_file, Path(args.inline_sign_file))
    if args.detach_sign_file:
        detach_sign(sign_key, unsigned_file, Path(args.detach_sign_file))
