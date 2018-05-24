"""GnuPG-related functions."""

import gnupg

from .utils import get_paths


class KeyRing(object):
    """The key ring is used to import GPG keys and return fingerprints."""

    def __init__(self):
        homedir = str(get_paths()['gnupghome'])
        self.gpg = gnupg.GPG(homedir=homedir)

    def import_key(self, key):
        """Import the given GPG key and return its fingerprint."""
        imported = self.gpg.import_keys(key)
        # Only return the last 8 chars of the fingerprint, since that's the
        # format used by reprepro.
        return imported.results[0]['fingerprint'][-8:]


def export_public_key(key_id, path, gnupghome=None):
    """Export a public key in ASCII format to the specified path."""
    if not gnupghome:
        gnupghome = str(get_paths()['gnupghome'])
    gpg = gnupg.GPG(homedir=gnupghome)
    material = gpg.export_keys(key_id)
    with path.open('w') as fh:
        fh.write(material)


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
