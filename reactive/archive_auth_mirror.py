from charmhelpers.core import hookenv

from charms.reactive import when, when_not

from charms.layer.nginx import configure_site
from charms.archive_auth_mirror import gpg, reprepro, utils


@when('nginx.available')
def configure_webapp():
    utils.install_resources()
    configure_static_serve()


@when('nginx.available', 'website.available')
def configure_website(website):
    website.configure(port=hookenv.config()['port'])


@when('config.changed.mirror-uri')
def config_mirror_uri_changed():
    configure_static_serve()


@when('config.set.mirror-uri', 'config.set.mirror-archs',
      'config.set.mirror-gpg-key', 'config.set.sign-gpg-key')
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
