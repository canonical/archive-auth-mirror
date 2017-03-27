import gnupg

from .utils import get_paths


def import_gpg_keys(mirror_key, sign_key, gnupghome=None):
    '''Import specified GPG keys returning their fingerprints.'''
    if not gnupghome:
        gnupghome = str(get_paths()['gnupghome'])

    gpg = gnupg.GPG(homedir=gnupghome)
    imported_mirror_key = gpg.import_keys(mirror_key)
    imported_sign_key = gpg.import_keys(sign_key)

    def fingerprint(imported):
        return imported.results[0]['fingerprint']

    return fingerprint(imported_mirror_key), fingerprint(imported_sign_key)
