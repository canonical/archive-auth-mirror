"""Install and configure archive-auth-mirror to mirror an Ubuntu repository."""

from charmhelpers.core import hookenv
from charms.layer.nginx import configure_site
from charms.reactive import (
    clear_flag,
    only_once,
    set_flag,
    when,
    when_not,
)

from charms.archive_auth_mirror import (
    repository,
    setup,
)
from archive_auth_mirror import (
    cron,
    gpg,
    mirror,
    ssh,
    utils,
)


# Define options requiring an nginx reconfiguration.
NGINX_OPTIONS = (
    'auth-cache-duration',
    'auth-cache-enabled',
    'auth-cache-inactivity',
    'resource-name',
)


def charm_flag(flag):
    """Return a reactive flag name for this charm."""
    return 'archive-auth-mirror.' + flag


@when_not(charm_flag('installed'))
def install():
    setup.install_resources()
    set_flag(charm_flag('installed'))


@when(charm_flag('installed'))
@only_once
def create_ssh_key():
    path = utils.get_paths()['ssh-key']
    if not path.exists():
        # only_once doesn't protect the handler from running if the line in
        # source code changes (so it can run again in an upgrade-charm hook)
        ssh.create_key(path)


@when('basic-auth-check.joined')
def reset_static_service(basic_auth_check):
    clear_flag(charm_flag('static-serve.configured'))


@when(charm_flag('installed'), 'nginx.available', 'basic-auth-check.changed')
@when_not(charm_flag('static-serve.configured'))
def configure_static_service(basic_auth_check):
    _configure_static_serve(auth_backends=basic_auth_check.backends())
    set_flag(charm_flag('static-serve.configured'))


@when(charm_flag('installed'), 'nginx.available')
@when_not(charm_flag('static-serve.configured'))
def configure_static_service_no_basic_auth_check():
    _configure_static_serve(auth_backends=[])
    set_flag(charm_flag('static-serve.configured'))


@when(charm_flag('installed'))
@when('nginx.available', 'website.available')
@when_not(charm_flag('website.configured'))
def configure_website(website):
    website.configure(port=hookenv.config()['port'])
    set_flag(charm_flag('website.configured'))


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


@when(charm_flag('static-serve.configured'), 'config.changed')
@when('basic-auth-check.available')
def config_changed_basic_auth(basic_auth_check):
    cfg = hookenv.config()
    if any(cfg.changed(option) for option in NGINX_OPTIONS):
        _configure_static_serve(auth_backends=basic_auth_check.backends())


@when(charm_flag('static-serve.configured'), 'config.changed')
@when_not('basic-auth-check.available')
def config_changed_no_basic_auth():
    cfg = hookenv.config()
    if any(cfg.changed(option) for option in NGINX_OPTIONS):
        _configure_static_serve(auth_backends=[])


@when(charm_flag('static-serve.configured'), 'basic-auth-check.changed')
def config_basic_auth_check_changed(basic_auth_check):
    _configure_static_serve(auth_backends=basic_auth_check.backends())


@when_not('basic-auth-check.available')
@when('basic-auth-check.changed')
def config_basic_auth_check_removed(basic_auth_check):
    _configure_static_serve(auth_backends=[])


@when(charm_flag('installed'), 'config.changed')
def config_set():
    config = hookenv.config()
    missing_options = setup.missing_options(config)
    if missing_options:
        hookenv.status_set(
            'blocked',
            'Mirroring is disabled as some configuration options are missing: '
            '{}'.format(', '.join(missing_options)))
        return

    # Configure mirroring.
    keyring = gpg.KeyRing()
    mirrors = mirror.from_config(
        keyring, config['mirrors'], config['repository-origin'].strip())
    sign_key_fingerprint = keyring.import_key(config['sign-gpg-key'])
    sign_key_passphrase = config.get('sign-gpg-passphrase', '').strip()
    repository.configure_reprepro(
        mirrors, sign_key_fingerprint, sign_key_passphrase)
    # Export the public key used to sign the repository.
    _export_sign_key(sign_key_fingerprint)
    hookenv.status_set('active', 'Mirroring configured')


@when_not('config.set.mirrors', 'config.set.sign-gpg-key')
def config_not_set():
    repository.disable_mirroring()
    hookenv.status_set(
        'blocked', 'Not all required configs set, mirroring is disabled')


@when_not(charm_flag('job.enabled'))
@when('leadership.is_leader')
def install_cron():
    cron.install_crontab()
    set_flag(charm_flag('job.enabled'))


@when_not('leadership.is_leader')
@when(charm_flag('job.enabled'))
def remove_cron():
    cron.remove_crontab()
    clear_flag(charm_flag('job.enabled'))


def _configure_static_serve(auth_backends=None):
    """Configure the static file serve."""
    cfg = hookenv.config()
    vhost_config = setup.get_virtualhost_config(
        auth_backends, cfg['resource-name'], cfg['auth-cache-enabled'],
        cfg['auth-cache-duration'], cfg['auth-cache-inactivity'])
    configure_site('archive-auth-mirror', 'nginx-static.j2', **vhost_config)


def _export_sign_key(key_id):
    """Export the public key for the repo under the static serve."""
    filename = utils.get_paths()['static'] / 'key.asc'
    gpg.export_public_key(key_id, filename)
