import textwrap
import unittest
from pathlib import Path

from fixtures import TempDir

from testtools.matchers import (
    FileContains,
    DirContains,
    Contains,
)

from charmtest import CharmTest

from charms.ubuntu_esm.utils import (
    get_paths,
    get_virtualhost_name,
    get_website_relation_config,
    install_resources,
)

from fakes import FakeHookEnv


class GetPathsTest(unittest.TestCase):

    def test_get_paths(self):
        '''get_paths returns service paths.'''
        paths = get_paths()
        self.assertEqual(
            {'base': Path('/srv/ubuntu-esm'),
             'bin': Path('/srv/ubuntu-esm/bin'),
             'reprepro': Path('/srv/ubuntu-esm/reprepro'),
             'static': Path('/srv/ubuntu-esm/static'),
             'gnupghome': Path('/srv/ubuntu-esm/reprepro/.gnupg')},
            paths)


class GetVirtualhostNameTest(unittest.TestCase):

    def test_get_no_config(self):
        '''If the 'service-url' config is not set, the unit IP is returned.'''
        hookenv = FakeHookEnv()
        self.assertEqual('1.2.3.4', get_virtualhost_name(hookenv=hookenv))

    def test_get_with_config(self):
        '''If the 'service-url' config is set, it's used as virtualhost.'''
        hookenv = FakeHookEnv(config={'service-url': 'example.com'})
        self.assertEqual('example.com', get_virtualhost_name(hookenv=hookenv))


class GetWebsiteRelationConfigTest(unittest.TestCase):

    def test_config(self):
        '''get_website_relation_config returns the relation configuration.'''
        config = get_website_relation_config('host.example.com')

        expected_site_config = textwrap.dedent('''
        <VirtualHost host.example.com:80>
          DocumentRoot "/srv/ubuntu-esm/static"

          <Location />
            Require all granted
            Options +Indexes
          </Location>
        </VirtualHost>
        ''')
        self.assertEqual(
            {'domain': 'host.example.com',
             'enabled': True,
             'site_config': expected_site_config,
             'site_modules': ['autoindex'],
             'ports': [80]},
            config)


class InstallResourcesTests(CharmTest):

    def setUp(self):
        super().setUp()
        self.base_dir = self.useFixture(TempDir())

    def test_dirs(self):
        '''The install_resources function creates the filesystem structure.'''
        install_resources(base_dir=self.base_dir.path)
        self.assertThat(
            self.base_dir.path, DirContains(['bin', 'static', 'reprepro']))

    def test_resources(self):
        '''Resources from the charm are copied to the service tree.'''
        install_resources(base_dir=self.base_dir.path)
        self.assertThat(
            self.base_dir.join('static/index.html'),
            FileContains(matcher=Contains("Ubuntu ESM")))
        self.assertThat(
            self.base_dir.join('bin/ubuntu-esm-mirror'),
            FileContains(matcher=Contains("reprepro")))
