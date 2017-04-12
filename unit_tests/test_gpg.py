from pathlib import Path

from charmtest import CharmTest

from archive_auth_mirror.utils import get_paths
from archive_auth_mirror.gpg import (
    import_keys,
    export_public_key,
    inline_sign,
    detach_sign,
)


PUBLIC_KEY_FINGERPRINT = 'E275C4776E00A6BAED081A97DE2922ADDC4EDFF2'
PUBLIC_KEY_MATERIAL = '''
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBFjYx6EBCADPQeJWE7247I7YVHQPgYsK9OtuHJmRGsJ6YUNOk+p3pX+r9r4d
CwBHoQcRJu+WAucsC09ow4o8CxwsdFdQ2RgFSioyGivoTR5Qwf3DUPBwgWJGRKLU
ajrrhL/t5SaYgIppZRSvTy9tt/SEa0LdUsdK2hLMWL6UDalJgdzKOTerE9MLuyVK
ygW4qld7gLYCyadOS3rhO5/+ygzy13jAMCpIGF0j0VVqmImJEtd4x0d2RPfOe2jO
xVVCdGicH7YPorycKgRY1jVU5bqb+4nvfd2Efx5zGAwENeF04mTEflC/zYBO1HaW
sHU2z2YIoyxCoxWQtUGVOCD5Q61Rhhst6LkDABEBAAG0ClNhbXBsZSBrZXmJATcE
EwEIACEFAljYx6ECGwMFCwkIBwIGFQgJCgsCBBYCAwECHgECF4AACgkQ3ikirdxO
3/KKOgf/fFJ62OBid/L47g4YN6TbIS9fQvzmU/ouveRJvRNGXJEr1ZxA+uGj4S0v
vfzmIBWmaQ89pd3hCwrhWq0enX1e7LChv1WBI76j1PSeSBYdJ7xp6W0Di05nQG9l
156FckZgYCAPE0cDDnFleL0F/6VkqXxWjq7H5nsBxP7VxuwHBYUdrzMztYkXLOf6
AKmVHRD6E3kdNSMnIGNTPa+VAVRiyqOq0/Jtbb82tbdme8Ra31ts2ZtzJ5CURWRd
Wv0xp5cTkxLhC5LyZk2j93kQCxhV09aJqijTicVtdz+Bxd4PLbkYN4omBUE0r9HR
WoWaHrg8YaU9w+hl3hBRiqpCD9/cDLkBDQRY2MehAQgAz+kIRwGd1m8wmTAmlqMo
BO1iY8eJ6bckD54Uik9Bx3rcJNacxk5kLNi/ZWHaqtnm7DiIQiLbHymi0vqjF4IB
8ZfnFh1veJ2PTwC7oXqSejyTcv4uIjGjLipcaIRTjNIG+jevxyLMpbskAZDLaSHv
HP50vrBe1r1VPzOuE0JZS8wSccoaYRR+O6qKWwTaIZv5pz8JiGHP8D+9lJyyGKqp
zGyi1tPuXcUkfjrqlUHdq/rCXxORXtUM30zEKyFyid/gmyuS6Q9hIU5AaNgYITYj
jBFRaO9JiNpVerHfsLfhWw1bx/gsRzDAg93V+DhnkVT4eClL2weasRw+4U5V1Pas
pQARAQABiQEfBBgBCAAJBQJY2MehAhsMAAoJEN4pIq3cTt/ypakH/0yBmWgaA+bP
5ArgP//KkWRnmIeeO+gp/Rp4XXb18V6h8DmLiY+nMHRdYslm8SXBFjOlfbdRKIdX
FxnhkRt8I6WSgsYk/90Abqr2cdblnKz7igFN7jdTvUI7CYlEIr+DR9sAKIaW8lmP
wL+5P/+r3g8M1BJ9lyDDdTPgI6PIqABpQIRex+FZETwP0fdIuC6AGskv0lNxN7OK
jQugeKt5fEyoxL/ncV1HBW2rHZgS6caLZ9rrA2bhngftH57DL9prQT+L6Is+QJar
X7j0r703KfTUogVbFc10dgSHEGvgIiKiuqM4dSqvmH8gIGu5b1lG7CrqWh9lHisf
E2Te61Dxbmc=
=RGEC
-----END PGP PUBLIC KEY BLOCK-----
'''

SECRET_KEY_FINGERPRINT = '838F411018AB1C7408B394F8964458199BF027F5'
SECRET_KEY_MATERIAL = '''
-----BEGIN PGP PRIVATE KEY BLOCK-----

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
FUB99LPi8uvx+QjcHLg=
=Hw32
-----END PGP PRIVATE KEY BLOCK-----
'''


class ImportKeysTest(CharmTest):

    def test_import_keys(self):
        """import_keys imports the mirror and sign keys."""
        fingerprints = import_keys(
            PUBLIC_KEY_MATERIAL, SECRET_KEY_MATERIAL,
            gnupghome=self.fakes.fs.root.path)
        # returned fingerprints are 8 characters long
        self.assertEqual(
            (PUBLIC_KEY_FINGERPRINT[-8:], SECRET_KEY_FINGERPRINT[-8:]),
            fingerprints)


class ExportPublicKeyTest(CharmTest):

    def test_export_public_key(self):
        """export_public_key exports the specified public key."""
        gnupghome = self.fakes.fs.root.path
        public_key_file = Path(self.fakes.fs.root.path) / 'public.asc'
        fingerprints = import_keys(
            PUBLIC_KEY_MATERIAL, SECRET_KEY_MATERIAL,
            gnupghome=gnupghome)
        export_public_key(
            fingerprints.sign, public_key_file, gnupghome=gnupghome)
        material = public_key_file.read_text()
        self.assertTrue(
            material.startswith('-----BEGIN PGP PUBLIC KEY BLOCK-----'))
        self.assertTrue(
            material.endswith('-----END PGP PUBLIC KEY BLOCK-----\n'))


class InlineSignTest(CharmTest):

    def test_inline_sign(self):
        """inline_sign creates an inline signature for a file."""
        paths = get_paths(root_dir=Path(self.fakes.fs.root.path))
        paths['gnupghome'].mkdir(parents=True)
        paths['sign-passphrase'].write_text('')

        fingerprints = import_keys(
            PUBLIC_KEY_MATERIAL, SECRET_KEY_MATERIAL,
            gnupghome=str(paths['gnupghome']))

        unsigned_file = Path(self.fakes.fs.root.join('unsigned'))
        unsigned_file.write_text('some text to sign')
        inline_sign_file = Path(self.fakes.fs.root.join('signed'))

        inline_sign(
            fingerprints[1], unsigned_file, inline_sign_file, paths=paths)

        signed_content = inline_sign_file.read_text()
        self.assertIn('some text to sign', signed_content)
        self.assertIn('-----BEGIN PGP SIGNATURE-----', signed_content)


class DetachSignTest(CharmTest):

    def test_detach_sign(self):
        """detach_sign creates a detached signature for a file."""
        paths = get_paths(root_dir=Path(self.fakes.fs.root.path))
        paths['gnupghome'].mkdir(parents=True)
        paths['sign-passphrase'].write_text('')

        fingerprints = import_keys(
            PUBLIC_KEY_MATERIAL, SECRET_KEY_MATERIAL,
            gnupghome=str(paths['gnupghome']))

        unsigned_file = Path(self.fakes.fs.root.join('unsigned'))
        unsigned_file.write_text('some text to sign')
        detach_sign_file = Path(self.fakes.fs.root.join('signature'))

        detach_sign(
            fingerprints[1], unsigned_file, detach_sign_file, paths=paths)

        signature = detach_sign_file.read_text()
        self.assertTrue(signature.startswith('-----BEGIN PGP SIGNATURE-----'))
        self.assertTrue(signature.endswith('-----END PGP SIGNATURE-----\n'))
