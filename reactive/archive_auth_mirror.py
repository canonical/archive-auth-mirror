from charmhelpers.core import hookenv

from charms.reactive import when, when_not, set_state, remove_state, only_once

from charms.layer.nginx import configure_site

from charms.archive_auth_mirror import repository, setup
from archive_auth_mirror import gpg, cron, ssh


def charm_state(state):
    """Convenience to return a reactive state name for this charm."""
    return 'archive-auth-mirror.{}'.format(state)


@when_not(charm_state('installed'))
def install():
    setup.install_resources()
    set_state(charm_state('installed'))


@when(charm_state('installed'))
@only_once
def create_ssh_key():
    ssh.create_key()


@when(charm_state('installed'), 'nginx.available')
def configure_webapp():
    _configure_static_serve()


@when(charm_state('installed'), 'nginx.available', 'website.available')
def configure_website(website):
    website.configure(port=hookenv.config()['port'])


@when_not('ssh-peers.local_public_key')
@when('ssh-peers.connected')
def set_ssh_key(ssh_keys):
    ssh_keys.set_local_public_key(ssh.get_public_key())


@when('ssh-peers.new_remote_public_key')
def add_authorized_key(ssh_keys):
    hookenv.log("Adding key: " + ssh_keys.get_authorized_key())
    remote_public_key = ssh_keys.get_authorized_key()
    ssh.add_authorized_key(remote_public_key)
    ssh_peer = {ssh_keys.get_remote('private-address'): remote_public_key}
    repository.update_config(new_ssh_peers=ssh_peer)
    ssh_keys.remove_state(ssh_keys.states.new_remote_public_key)


@when(charm_state('installed'), 'config.changed.mirror-uri')
def config_mirror_uri_changed():
    _configure_static_serve()


@when(charm_state('installed'), 'config.changed')
def config_set():
    config = hookenv.config()
    if not setup.have_required_config(config):
        return

    # configure mirroring
    mirror_fprint, sign_fprint = gpg.import_gpg_keys(
        config['mirror-gpg-key'], config['sign-gpg-key'])
    sign_gpg_passphrase = config.get('sign-gpg-passphrase', '').strip()
    repository.configure_reprepro(
        config['mirror-uri'].strip(), config['mirror-archs'].strip(),
        mirror_fprint, sign_fprint, sign_gpg_passphrase)
    hookenv.status_set('active', 'Mirroring configured')


@when_not('config.set.mirror-uri', 'config.set.mirror-archs',
          'config.set.mirror-gpg-key', 'config.set.sign-gpg-key')
def config_not_set():
    repository.disable_mirroring()
    hookenv.status_set(
        'blocked', 'Not all required configs set, mirroring is disabled')


@when_not(charm_state('job.enabled'))
@when('leadership.is_leader')
def install_cron():
    cron.install_crontab()
    set_state(charm_state('job.enabled'))


@when_not('leadership.is_leader')
@when(charm_state('job.enabled'))
def remove_cron():
    cron.remove_crontab()
    remove_state(charm_state('job.enabled'))


def _configure_static_serve():
    """Configure the static file serve."""
    vhost_config = setup.get_virtualhost_config()
    configure_site(
        'archive-auth-mirror', 'nginx-static.j2', **vhost_config)
