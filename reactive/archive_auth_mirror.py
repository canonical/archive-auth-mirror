
from charms.reactive import (
    when,
    when_not,
    set_state,
)
from charmhelpers.core import hookenv
from charmhelpers.fetch import apt_install

from charms.archive_auth_mirror.utils import (
    configure_website_relation,
    get_website_relation_config,
    install_resources,
)

from charms.archive_auth_mirror import gpg, reprepro


PACKAGES = ['reprepro']


@when_not('archive-auth-mirror.installed')
def install():
    apt_install(PACKAGES, fatal=True)
    install_resources()
    set_state('archive-auth-mirror.installed')


@when('config.changed.service-url')
def config_service_url():
    configure_website_relation()


@when('config.changed')
def config_changed():
    config = hookenv.config()
    mirror_uri = config.get('mirror-uri')
    mirror_archs = config.get('mirror-archs')
    mirror_key = config.get('mirror-gpg-key')
    sign_key = config.get('sign-gpg-key')

    if mirror_uri and mirror_archs and mirror_key and sign_key:
        mirror_fprint, sign_fprint = gpg.import_gpg_keys(mirror_key, sign_key)
        reprepro.configure_reprepro(
            mirror_uri, mirror_archs, mirror_fprint, sign_fprint)
        hookenv.log('Configured mirroring')
    else:
        reprepro.disable_mirroring()
        hookenv.log('Not all required configs set, mirroring is disabled')


@when('static-website.available')
def static_website_relation(apache):
    domain = hookenv.unit_public_ip()
    config = get_website_relation_config(domain)
    apache.send_domain(config['domain'])
    apache.send_site_config(config['site_config'])
    apache.send_site_modules(config['site_modules'])
    apache.send_ports(config['ports'])
    apache.send_enabled()
