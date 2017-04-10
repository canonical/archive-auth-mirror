#!/usr/bin/env python3

import sys
import subprocess
import argparse

from ..utils import get_paths
from ..script import (
    setup_logger,
    get_config,
)


def gpg(args, sign_key_id, paths=None):
    """Call gpg with the specified args."""
    if paths is None:
        paths = get_paths()
    command = [
        'gpg', '--no-use-agent', '--batch',
        '--passphrase-file', str(paths['sign-passphrase']),
        '--homedir', str(paths['gnupghome']), '-u', sign_key_id]
    command.extend(args)
    subprocess.check_call(command)


def inline_sign(unsigned_file, inline_sign_file, sign_key_id):
    """Create an inline-signed file."""
    gpg(
        ['-o', inline_sign_file, '--clearsign', '-a', unsigned_file],
        sign_key_id)


def detach_sign(unsigned_file, detach_sign_file, sign_key_id):
    """Create a detached signature for a file."""
    gpg(
        ['-o', detach_sign_file, '--detach-sig', '-a', unsigned_file],
        sign_key_id)


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
    args = parse_args()
    if args.inline_sign_file:
        inline_sign(
            args.unsigned_file, args.inline_sign_file, config['sign-key-id'])
    if args.detach_sign_file:
        detach_sign(
            args.unsigned_file, args.detach_sign_file, config['sign-key-id'])
