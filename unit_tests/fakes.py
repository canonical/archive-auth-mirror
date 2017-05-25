"""Fakes for unittests."""


class FakeHookEnv:
    """A fake hookenv object."""

    def __init__(self, config=None):
        self._config = config or {}

    def config(self):
        return self._config

    def service_name(self):
        return 'service'

    def local_unit(self):
        return 'service/0'

    def unit_public_ip(self):
        return '1.2.3.4'

    def unit_private_ip(self):
        return '5.6.7.8'
