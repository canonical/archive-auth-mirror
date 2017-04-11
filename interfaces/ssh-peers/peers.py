from charmhelpers.core import hookenv
from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes
from charms.reactive import bus


class SshPeers(RelationBase):
    scope = scopes.UNIT

    class states(bus.StateList):
        connected = bus.State('{relation_name}.connected')
        local_public_key = bus.State('{relation_name}.local_public_key')
        new_remote_public_key = bus.State(
            '{relation_name}.new_remote_public_key')

    @hook('{peers:ssh-peers}-relation-{joined}')
    def joined(self):
        self.set_state(self.states.connected)

    @hook('{peers:ssh-peers}-relation-{changed,joined}')
    def changed(self):
        authorized_key = self.get_authorized_key()
        new_remote_public_key = self.get_remote('public-ssh-key')
        if not new_remote_public_key:
            hookenv.log("No remote public key set")
            self.remove_state(self.states.new_remote_public_key)
        else:
            if new_remote_public_key != authorized_key:
                hookenv.log("New remote public key")
                self.set_local('authorized-key', new_remote_public_key)
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
