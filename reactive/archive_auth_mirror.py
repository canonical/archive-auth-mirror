from charmhelpers.core import hookenv

from charms.reactive import when, when_not, set_state, remove_state

from charms.layer.nginx import configure_site

from charms.archive_auth_mirror import repository, setup
from archive_auth_mirror import gpg, cron


def charm_state(state):
    """Convenience to return a reactive state name for this charm."""
    return 'archive-auth-mirror.{}'.format(state)


@when_not(charm_state('installed'))
def install():
    setup.install_resources()
    set_state(charm_state('installed'))


@when(charm_state('installed'), 'nginx.available')
@when_not(charm_state('static-serve.configured'))
def configure_static_service():
    _configure_static_serve()
    set_state(charm_state('static-serve.configured'))


@when(charm_state('installed'))
@when('nginx.available', 'website.available')
@when_not(charm_state('website.configured'))
def configure_website(website):
    website.configure(port=hookenv.config()['port'])
    set_state(charm_state('website.configured'))


@when(charm_state('static-serve.configured'), 'config.changed.mirror-uri')
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
