from pathlib import Path
from unittest import TestCase

import yaml

from charmtest import CharmTest

from archive_auth_mirror.utils import get_paths, get_config, update_config


class GetPathsTest(TestCase):

    def test_get_paths(self):
        """get_paths returns service paths."""
        paths = get_paths()
        self.assertEqual(
            {'base': Path('/srv/archive-auth-mirror'),
             'cron': Path('/etc/cron.d/archive-auth-mirror'),
             'bin': Path('/srv/archive-auth-mirror/bin'),
             'config': Path('/srv/archive-auth-mirror/config.yaml'),
             'static': Path('/srv/archive-auth-mirror/static'),
             'basic-auth': Path('/srv/archive-auth-mirror/basic-auth'),
             'sign-passphrase': Path(
                 '/srv/archive-auth-mirror/sign-passphrase'),
             'ssh-key': Path('/srv/archive-auth-mirror/ssh-key'),
             'authorized-keys': Path('/root/.ssh/authorized_keys'),
             'lockfile': Path('/srv/archive-auth-mirror/mirror-archive.lock'),
             'reprepro': Path('/srv/archive-auth-mirror/reprepro'),
             'reprepro-conf': Path('/srv/archive-auth-mirror/reprepro/conf'),
             'gnupghome': Path('/srv/archive-auth-mirror/reprepro/.gnupg')},
            paths)


class GetConfigTest(CharmTest):

    def test_config_not_found(self):
        """If the config file is not found, get_config returns {}."""
        self.assertEqual({}, get_config(config_path=Path('/not/here')))

    def test_load_config(self):
        """If the file is found, it's content is returned as YAML."""
        tempdir = Path(self.fakes.fs.root.path)
        config_path = tempdir / 'config.yaml'

        config = {'value1': 30, 'value2': 'foo'}
        with config_path.open('w') as fh:
            yaml.dump(config, stream=fh)
        self.assertEqual(config, get_config(config_path=config_path))


class UpdateConfigTest(CharmTest):

    def setUp(self):
        super().setUp()
        self.config_path = Path(self.fakes.fs.root.path) / 'config.yaml'

    def test_no_config(self):
        """update_config creates the config file if not present."""
        update_config(config_path=self.config_path, suite='precise')
        self.assertTrue(self.config_path.exists())
        self.assertEqual(
            {'suite': 'precise'}, get_config(config_path=self.config_path))

    def test_update_existing(self):
        """update_config updates the config file if it exists."""
        update_config(config_path=self.config_path, suite='precise')
        update_config(config_path=self.config_path, sign_key_id='AABBCC')
        self.assertEqual(
            {'suite': 'precise', 'sign-key-id': 'AABBCC'},
            get_config(config_path=self.config_path))

    def test_update_ssh_peers(self):
        """update_config adds new ssh-peers."""
        update_config(
            config_path=self.config_path, new_ssh_peers={'1.2.3.4': 'aabb'})
        update_config(
            config_path=self.config_path, new_ssh_peers={'5.6.7.8': 'ccdd'})
        self.assertEqual(
            {'ssh-peers': {
                '1.2.3.4': 'aabb',
                '5.6.7.8': 'ccdd'}},
            get_config(config_path=self.config_path))
