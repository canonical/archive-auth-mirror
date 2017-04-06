from charmhelpers.core import hookenv
from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes
from charms.reactive import bus


class SshKeysPeers(RelationBase):
    scope = scopes.UNIT

    class states(bus.StateList):
        connected = bus.State('{relation_name}.connected')
        authorized_key = bus.State('{relation_name}.authorized_key')

    @hook('{peers:ssh-keys}-relation-{changed,joined}')
    def changed(self):
        authorized_key = self.get_authorized_key()
        public_key = self.get_remote('public-ssh-key')
        if not public_key:
            hookenv.log("No public key set")
            self.remove_state(self.states.authorized_key)
        else:
            if public_key != authorized_key:
                hookenv.log("New public key")
                self.set_local('authorized-key', public_key)
                self.set_state(self.states.authorized_key)
            else:
                hookenv.log("Public key is still the same")
        hookenv.log(repr(self.get_authorized_key()))
        self.set_state(self.states.connected)

    @hook('{peers:ssh-keys}-relation-{departed}')
    def departed(self):
        # Remove the state that our relationship is now connected to our
        # principal layer(s)
        self.remove_state(self.states.connected)

    def set_public_key(self, public_key):
        relation_info = {'public-ssh-key': public_key}
        self.set_remote(**relation_info)

    def get_authorized_key(self):
        return self.get_local('authorized-key')
