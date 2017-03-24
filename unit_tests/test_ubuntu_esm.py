import os
import textwrap
import unittest
from fixtures import TempDir

from charmtest import CharmTest

import ubuntu_esm


class InstallResourcesTests(CharmTest):

    def setUp(self):
        super().setUp()
        self.base_dir = self.useFixture(TempDir()).path

    def test_dirs(self):
        '''The _install_resources function creates the filesystem structure.'''
        ubuntu_esm._install_resources(base_dir=self.base_dir)
        self.assertItemsEqual(
            ['bin', 'static', 'reprepro'],
            os.listdir(self.base_dir))

    def test_resources(self):
        '''Resources from the charm are copied to the service tree.'''
        ubuntu_esm._install_resources(base_dir=self.base_dir)
        with open(os.path.join(self.base_dir, 'static/index.html')) as fd:
            self.assertIn("Ubuntu ESM", fd.read())
        with open(os.path.join(self.base_dir, 'bin/ubuntu-esm-mirror')) as fd:
            self.assertIn("reprepro", fd.read())


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
