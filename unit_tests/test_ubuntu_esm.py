import os

from charmtest import CharmTest

from reactive import ubuntu_esm


class InstallResourcesTests(CharmTest):

    def test_dirs(self):
        '''The _install_resources function creates the filesystem structure.'''
        root_path = self.fakes.fs.root.path
        self.fakes.fs.add('/srv')
        ubuntu_esm._install_resources()
        print(os.listdir(root_path))
