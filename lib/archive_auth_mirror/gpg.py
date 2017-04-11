"""GnuPG-related functions."""

from collections import namedtuple

import gnupg

from .utils import get_paths


Fingerprints = namedtuple('Fingerprints', ['mirror', 'sign'])


def import_keys(mirror_key, sign_key, gnupghome=None):
    """Import specified GPG keys returning their fingerprints."""
    if not gnupghome:
        gnupghome = str(get_paths()['gnupghome'])
    gpg = gnupg.GPG(homedir=gnupghome)

    imported_mirror_key = gpg.import_keys(mirror_key)
    imported_sign_key = gpg.import_keys(sign_key)

    def fingerprint(imported):
        # only return the last 8 chars of the fingerprint, since that's the
        # format used by reprepro
        return imported.results[0]['fingerprint'][-8:]

    return Fingerprints(
        fingerprint(imported_mirror_key), fingerprint(imported_sign_key))


def inline_sign(key_id, unsigned_file, inline_sign_file, paths=None):
    """Create an inline-signed file."""
    _sign(
        key_id, unsigned_file, inline_sign_file, paths,
        clearsign=True, detach=False)


def detach_sign(key_id, unsigned_file, detach_sign_file, paths=None):
    """Create a detached signature for a file."""
    _sign(
        key_id, unsigned_file, detach_sign_file, paths,
        clearsign=False, detach=True)


def _sign(key_id, in_file, out_file, paths, **sign_options):
    if paths is None:
        paths = get_paths()
    gpg = gnupg.GPG(homedir=str(paths['gnupghome']))

    passphrase = paths['sign-passphrase'].read_text().strip()

    with in_file.open() as in_fh:
        sign = gpg.sign(in_fh, default_key=key_id, passphrase=passphrase,
                        **sign_options)
        out_file.write_text(str(sign))
