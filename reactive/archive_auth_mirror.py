"""Install and configure archive-auth-mirror to mirror an Ubuntu repository."""

from charmhelpers.core import hookenv

from charms.reactive import when, when_not, set_state, remove_state, only_once

from charms.layer.nginx import configure_site

from charms.archive_auth_mirror import repository, setup
from archive_auth_mirror import gpg, cron, ssh, utils


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
    path = utils.get_paths()['ssh-key']
    if not path.exists():
        # only_once doesn't protect the handler from running if the line in
        # source code changes (so it can run again in an upgrade-charm hook)

        ssh.create_key(path)


@when(charm_state('installed'),
      'nginx.available',
      'basic-auth-check.changed')
@when_not(charm_state('static-serve.configured'))
def configure_static_service(basic_auth_check):
    _configure_static_serve(auth_backends=basic_auth_check.backends())
    set_state(charm_state('static-serve.configured'))


@when(charm_state('installed'))
@when('nginx.available', 'website.available')
@when_not(charm_state('website.configured'))
def configure_website(website):
    website.configure(port=hookenv.config()['port'])
    set_state(charm_state('website.configured'))


@when_not('ssh-peers.local-public-key')
@when('ssh-peers.connected')
def set_ssh_key(ssh_keys):
    public_key_path = str(utils.get_paths()['ssh-key']) + '.pub'
    with open(public_key_path, 'r') as public_key_file:
        public_key = public_key_file.read()
    ssh_keys.set_local_public_key(public_key)


@when('ssh-peers.new-remote-public-key')
def add_authorized_key(ssh_keys):
    remote_public_key = ssh_keys.get_remote('public-ssh-key')
    hookenv.log("Adding key: " + remote_public_key)
    ssh.add_authorized_key(
        remote_public_key, utils.get_paths()['authorized-keys'])
    ssh_peer = {ssh_keys.get_remote('private-address'): remote_public_key}
    utils.update_config(
        config_path=utils.get_paths()['config'], new_ssh_peers=ssh_peer)
    ssh_keys.remove_state(ssh_keys.states.new_remote_public_key)


@when(charm_state('static-serve.configured'), 'config.changed.mirror-uri')
@when_not('basic-auth-check.available')
def config_mirror_uri_changed_no_basic_auth():
    _configure_static_serve(auth_backends=[])


@when(charm_state('static-serve.configured'), 'config.changed.mirror-uri')
@when('basic-auth-check.available')
def config_mirror_uri_changed_basic_auth(basic_auth_check):
    _configure_static_serve(auth_backends=basic_auth_check.backends())


@when(charm_state('static-serve.configured'), 'config.changed.auth-cache-time')
@when_not('basic-auth-check.available')
def config_auth_cache_time_changed_no_basic_auth():
    _configure_static_serve(auth_backends=[])


@when(charm_state('static-serve.configured'), 'config.changed.auth-cache-time')
@when('basic-auth-check.available')
def config_auth_cache_time_changed_basic_auth(basic_auth_check):
    _configure_static_serve(auth_backends=basic_auth_check.backends())


@when(charm_state('static-serve.configured'), 'basic-auth-check.changed')
def config_basic_auth_check_changed(basic_auth_check):
    _configure_static_serve(auth_backends=basic_auth_check.backends())


@when_not('basic-auth-check.available')
@when('basic-auth-check.changed')
def config_basic_auth_check_removed(basic_auth_check):
    _configure_static_serve(auth_backends=[])


@when(charm_state('installed'), 'config.changed')
def config_set():
    config = hookenv.config()
    if not setup.have_required_config(config):
        return

    # configure mirroring
    fingerprints = gpg.import_keys(
        config['mirror-gpg-key'], config['sign-gpg-key'])
    sign_gpg_passphrase = config.get('sign-gpg-passphrase', '').strip()
    repository_version = config.get('repository-version', '').strip()
    repository.configure_reprepro(
        config['mirror-uri'].strip(), config['mirror-archs'].strip(),
        fingerprints.mirror, fingerprints.sign, sign_gpg_passphrase,
        config['repository-origin'].strip(), repository_version)
    # export the public key used to sign the repository
    _export_sign_key(fingerprints.sign)
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


def _configure_static_serve(auth_backends=None):
    """Configure the static file serve."""
    auth_cache_time = hookenv.config()['auth-cache-time']
    vhost_config = setup.get_virtualhost_config(
        auth_backends=auth_backends, auth_cache_time=auth_cache_time)
    configure_site(
        'archive-auth-mirror', 'nginx-static.j2', **vhost_config)


def _export_sign_key(key_id):
    """Export the public key for the repo under the static serve."""
    filename = utils.get_paths()['static'] / 'key.asc'
    gpg.export_public_key(key_id, filename)
