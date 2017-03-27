'''Fakes for unittests.'''


class FakeHookEnv:
    '''A fake hookenv object.'''

    def __init__(self, config=None):
        self._config = config or {}

    def config(self):
        return self._config

    def unit_public_ip(self):
        return '1.2.3.4'
