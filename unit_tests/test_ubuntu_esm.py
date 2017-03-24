import os
import textwrap
import unittest

from charmtest import CharmTest

import ubuntu_esm


class InstallResourcesTests(CharmTest):

    pass

    # def test_dirs(self):
    #     '''The _install_resources function creates the filesystem structure.'''
    #     root_path = self.fakes.fs.root.path
    #     self.fakes.fs.add('/srv')
    #     ubuntu_esm._install_resources()
    #     print(os.listdir(root_path))


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
