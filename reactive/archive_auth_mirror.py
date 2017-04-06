from charmhelpers.core import hookenv

from charms.reactive import when, when_not, set_state, only_once

from charms.layer.nginx import configure_site
from charms.archive_auth_mirror import gpg, reprepro, utils, ssh


def charm_state(state):
    """Convenience to return a reactive state name for this charm."""
    return 'archive-auth-mirror.{}'.format(state)


@when_not(charm_state('installed'))
def install():
    utils.install_resources()
    set_state(charm_state('installed'))


@when(charm_state('installed'))
@only_once
def create_ssh_key():
    utils.install_resources()
    ssh.create_key()


@when(charm_state('installed'), 'nginx.available')
def configure_webapp():
    configure_static_serve()


@when(charm_state('installed'), 'nginx.available', 'website.available')
def configure_website(website):
    website.configure(port=hookenv.config()['port'])


@when(charm_state('installed'), 'config.changed.mirror-uri')
def config_mirror_uri_changed():
    configure_static_serve()


@when(charm_state('installed'), 'config.changed')
def config_set():
    config = hookenv.config()
    if not utils.have_required_config(config):
        return

    # configure mirroring
    mirror_fprint, sign_fprint = gpg.import_gpg_keys(
        config['mirror-gpg-key'], config['sign-gpg-key'])
    sign_gpg_passphrase = config.get('sign-gpg-passphrase', '').strip()
    reprepro.configure_reprepro(
        config['mirror-uri'].strip(), config['mirror-archs'].strip(),
        mirror_fprint, sign_fprint, sign_gpg_passphrase)
    hookenv.status_set('active', 'Mirroring configured')


@when_not('config.set.mirror-uri', 'config.set.mirror-archs',
          'config.set.mirror-gpg-key', 'config.set.sign-gpg-key')
def config_not_set():
    reprepro.disable_mirroring()
    hookenv.status_set(
        'blocked', 'Not all required configs set, mirroring is disabled')


def configure_static_serve():
    """Configure the static file serve."""
    vhost_config = utils.get_virtualhost_config()
    configure_site(
        'archive-auth-mirror', 'nginx-static.j2', **vhost_config)
