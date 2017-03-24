import textwrap
import unittest

from fixtures import TempDir

from testtools.matchers import (
    FileContains,
    DirContains,
    Contains,
)

from charmtest import CharmTest

import ubuntu_esm


class InstallResourcesTests(CharmTest):

    def setUp(self):
        super().setUp()
        self.base_dir = self.useFixture(TempDir())

    def test_dirs(self):
        '''The _install_resources function creates the filesystem structure.'''
        ubuntu_esm._install_resources(base_dir=self.base_dir.path)
        self.assertThat(
            self.base_dir.path, DirContains(['bin', 'static', 'reprepro']))

    def test_resources(self):
        '''Resources from the charm are copied to the service tree.'''
        ubuntu_esm._install_resources(base_dir=self.base_dir.path)
        self.assertThat(
            self.base_dir.join('static/index.html'),
            FileContains(matcher=Contains("Ubuntu ESM")))
        self.assertThat(
            self.base_dir.join('bin/ubuntu-esm-mirror'),
            FileContains(matcher=Contains("reprepro")))


class GetWebsiteRelationConfigTest(unittest.TestCase):

    def test_config(self):
        '''_get_website_relation_config returns the relation configuration.'''
        config = ubuntu_esm._get_website_relation_config('host.example.com')

        expected_site_config = textwrap.dedent('''
        <VirtualHost host.example.com:80>
          DocumentRoot "/srv/ubuntu-esm/static"
          Options +Indexes

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
             'ports': '80'},
            config)
