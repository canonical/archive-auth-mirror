import unittest

import yaml

from archive_auth_mirror.mirror import (
    from_config,
    Mirror,
)


class KeyRing(object):
    """A key ring used for tests."""

    def __init__(self, bad=False):
        self._bad = bad

    def import_key(self, key):
        if self._bad:
            raise TypeError('bad wolf')
        return key + '-fingerprint'


class TestFromConfig(unittest.TestCase):

    tests = [{
        'about': 'invalid yaml',
        'mirrors': ':',
        'want_error': 'cannot YAML decode mirrors value: ',
    }, {
        'about': 'invalid mirrors',
        'mirrors': '42',
        'want_error': 'mirrors value is not a list',
    }, {
        'about': 'invalid entry in mirrors',
        'mirrors': '["bad wolf"]',
        'want_error': 'mirrors value is not a list of maps',
    }, {
        'about': 'missing deb-line',
        'mirrors': yaml.safe_dump([{
            'pub-key': 'pub',
        }]),
        'want_error': "mirrors value is missing keys: 'deb-line'",
    }, {
        'about': 'missing pub-key',
        'mirrors': yaml.safe_dump([{
            'deb-line': 'https://user:pass@1.2.3.4/ubuntu bionic main misc',
        }]),
        'want_error': "mirrors value is missing keys: 'pub-key'",
    }, {
        'about': 'invalid deb-line',
        'mirrors': yaml.safe_dump([{
            'deb-line': 'https://user:pass@1.2.3.4/ubuntu',
            'pub-key': 'pub',
        }]),
        'want_error': "invalid debline 'https://user:pass@1.2.3.4/ubuntu'",
    }, {
        'about': 'invalid GPG key',
        'keyring': KeyRing(bad=True),
        'mirrors': yaml.safe_dump([{
            'deb-line': 'https://user:pass@1.2.3.4/ubuntu bionic main misc',
            'pub-key': 'pub',
        }]),
        'want_error': "cannot import GPG public key 'pub': bad wolf",
    }, {
        'about': 'success',
        'keyring': KeyRing(),
        'mirrors': yaml.safe_dump([{
            'deb-line': 'https://user:pass@1.2.3.4/ubuntu bionic main misc',
            'pub-key': 'pub1',
            'version': '18.10',
            'pocket': 'bionic-updates',
        }, {
            'deb-line': 'https://user:pass@4.3.2.1/ubuntu xenial main',
            'pub-key': 'pub2',
            'archs': 'i386',
        }]),
        'want_results': (
            Mirror(
                url='https://user:pass@1.2.3.4/ubuntu',
                suite='bionic',
                components='main misc',
                key='pub1-fingerprint',
                archs='source i386 amd64',
                version='18.10',
                origin='Ubuntu',
                pocket='bionic-updates',
            ),
            Mirror(
                url='https://user:pass@4.3.2.1/ubuntu',
                suite='xenial',
                components='main',
                key='pub2-fingerprint',
                archs='i386',
                version='',
                origin='Ubuntu',
                pocket='xenial',
            ),
        ),
    }, {
        'about': 'success with single mirror and different origin',
        'keyring': KeyRing(),
        'mirrors': yaml.safe_dump([{
            'deb-line': 'https://user:pass@1.2.3.4/ubuntu bionic main misc',
            'pub-key': 'pub1',
            'version': '18.10',
        }]),
        'origin': 'Gallifrey',
        'want_results': (
            Mirror(
                url='https://user:pass@1.2.3.4/ubuntu',
                suite='bionic',
                components='main misc',
                key='pub1-fingerprint',
                archs='source i386 amd64',
                version='18.10',
                origin='Gallifrey',
                pocket='bionic',
            ),
        ),
    }]

    def test_from_config(self):
        """Mirrors are generated from the config content."""
        for test in self.tests:
            with self.subTest(test['about']):
                self.check(
                    test.get('keyring'),
                    test['mirrors'],
                    test.get('origin', 'Ubuntu'),
                    test.get('want_results'),
                    test.get('want_error'),
                )

    def check(self, keyring, mirrors, origin, want_results, want_error):
        if want_error:
            with self.assertRaises(ValueError) as ctx:
                from_config(keyring, mirrors, origin)
            self.assertIn(want_error, str(ctx.exception))
            return
        results = from_config(keyring, mirrors, origin)
        self.assertEqual(results, want_results)
