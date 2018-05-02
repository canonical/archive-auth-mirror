from charmhelpers.core import hookenv
from charms.reactive import (
    flags,
    hook,
    RelationBase,
    scopes,
)


class SshPeers(RelationBase):
    """Allow public ssh keys to be propagated among units.

    When a new peer connects, a new secret SSH key should be created,
    and public key should be propagated to the peer using
    set_local_public_key()

    The peer will then be notified about the public key and can add it
    to its authorized_keys file.
    """

    scope = scopes.UNIT

    class states(flags.StateList):
        connected = flags.State('{relation_name}.connected')
        local_public_key = flags.State('{relation_name}.local-public-key')
        new_remote_public_key = flags.State(
            '{relation_name}.new-remote-public-key')

    @hook('{peers:ssh-peers}-relation-{joined}')
    def joined(self):
        self.set_state(self.states.connected)

    @hook('{peers:ssh-peers}-relation-{changed,joined}')
    def changed(self):
        previous_remote_public_key = self.get_local('remote-public-ssh-key')
        new_remote_public_key = self.get_remote('public-ssh-key')
        if not new_remote_public_key:
            hookenv.log("No remote public key set")
            self.remove_state(self.states.new_remote_public_key)
            return

        if new_remote_public_key != previous_remote_public_key:
            hookenv.log("New remote public key")
            self.set_local('remote-public-ssh-key', new_remote_public_key)
            self.set_state(self.states.new_remote_public_key)
        else:
            hookenv.log("Remote public key is still the same")

    @hook('{peers:ssh-peers}-relation-{departed}')
    def departed(self):
        # Remove the state that our relationship is now connected to our
        # principal layer(s)
        self.remove_state(self.states.connected)

    def set_local_public_key(self, public_key):
        relation_info = {'public-ssh-key': public_key}
        self.set_state(self.states.local_public_key)
        self.set_remote(**relation_info)
