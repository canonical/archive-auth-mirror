from charmtest import CharmTest

from reactive import ubuntu_esm


class SampleTest(CharmTest):

    def test_foo(self):
        print(ubuntu_esm)
        self.assertTrue(True)
