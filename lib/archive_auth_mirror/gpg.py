import gnupg

from .utils import get_paths


def import_gpg_keys(mirror_key, sign_key, gnupghome=None):
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

    return fingerprint(imported_mirror_key), fingerprint(imported_sign_key)
