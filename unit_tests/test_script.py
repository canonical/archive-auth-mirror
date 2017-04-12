from pathlib import Path

import yaml

from charmtest import CharmTest

from archive_auth_mirror.script import get_config


class GetConfigTest(CharmTest):

    def test_config_not_found(self):
        """If the config file is not found, get_config returns {}."""
        self.assertEqual({}, get_config(Path('/not/here')))

    def test_load_config(self):
        """If the file is found, it's content is returned as YAML."""
        tempdir = Path(self.fakes.fs.root.path)
        config_file = tempdir / 'config.yaml'

        config = {'value1': 30, 'value2': 'foo'}
        with config_file.open('w') as fh:
            yaml.dump(config, stream=fh)
        self.assertEqual(config, get_config(config_file))
