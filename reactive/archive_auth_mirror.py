from charmhelpers.core import hookenv

from charms.reactive import when, when_not, set_state

from charms.layer.nginx import configure_site
from charms.archive_auth_mirror import gpg, reprepro, utils


def charm_state(state):
    """Convenience to return a reactive state name for this charm."""
    return 'archive-auth-mirror.{}'.format(state)


@when_not(charm_state('installed'))
def install():
    utils.install_resources()
    set_state(charm_state('installed'))


@when(charm_state('installed'), 'nginx.available')
def configure_webapp():
    configure_static_serve()


@when(charm_state('installed'), 'nginx.available', 'website.available')
def configure_website(website):
    website.configure(port=hookenv.config()['port'])


@when(charm_state('installed'), 'config.changed.mirror-uri')
def config_mirror_uri_changed():
    configure_static_serve()


@when(charm_state('installed'), 'config.set.mirror-uri',
      'config.set.mirror-archs', 'config.set.mirror-gpg-key',
      'config.set.sign-gpg-key')
def config_set():
    config = hookenv.config()

    # configure mirroring
    mirror_fprint, sign_fprint = gpg.import_gpg_keys(
        config['mirror-gpg-key'], config['sign-gpg-key'])
    reprepro.configure_reprepro(
        config['mirror-uri'], config['mirror-archs'], mirror_fprint,
        sign_fprint)
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
