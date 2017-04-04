from unittest import TestCase, mock

from archive_auth_mirror.scripts.reprepro_sign_helper import (
    gpg,
    inline_sign,
    detach_sign,
)


class GPGCallsTest(TestCase):

    @mock.patch('subprocess.check_call')
    def test_gpg(self, mock_check_call):
        """gpg invokes the system gpg binary, with appropriate arguments."""
        gpg(['--other', 'options'], 'ABABAB')
        mock_check_call.assert_called_with(
            ['gpg', '--no-use-agent', '--batch', '--passphrase-file',
             '/srv/archive-auth-mirror/sign-passphrase', '--homedir',
             '/srv/archive-auth-mirror/reprepro/.gnupg', '-u', 'ABABAB',
             '--other', 'options'])

    @mock.patch('subprocess.check_call')
    def test_inline_sign(self, mock_check_call):
        """The inline_sign function calls gpg to sign a file inline."""
        inline_sign('unsigned.file', 'signed.file', 'ABABAB')
        mock_check_call.assert_called_with(
            ['gpg', '--no-use-agent', '--batch', '--passphrase-file',
             '/srv/archive-auth-mirror/sign-passphrase', '--homedir',
             '/srv/archive-auth-mirror/reprepro/.gnupg', '-u', 'ABABAB',
             '-o', 'signed.file', '--clearsign', '-a', 'unsigned.file'])

    @mock.patch('subprocess.check_call')
    def test_detach_sign(self, mock_check_call):
        """The detach_sign function calls gpg make a detached signature."""
        detach_sign('unsigned.file', 'signature.file', 'ABABAB')
        mock_check_call.assert_called_with(
            ['gpg', '--no-use-agent', '--batch', '--passphrase-file',
             '/srv/archive-auth-mirror/sign-passphrase', '--homedir',
             '/srv/archive-auth-mirror/reprepro/.gnupg', '-u', 'ABABAB',
             '-o', 'signature.file', '--detach-sig', '-a', 'unsigned.file'])
