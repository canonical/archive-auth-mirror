
from charms.reactive import (
    when,
    when_not,
    set_state,
)
from charmhelpers.core import hookenv
from charmhelpers.fetch import apt_install

from charms.ubuntu_esm.utils import (
    configure_website_relation,
    get_website_relation_config,
    install_resources,
)

from charms.ubuntu_esm.gpg import import_gpg_keys

PACKAGES = ['reprepro']


@when_not('ubuntu-esm.installed')
def install():
    apt_install(PACKAGES, fatal=True)
    install_resources()
    set_state('ubuntu-esm.installed')


@when('config.changed.service-url')
def config_service_url():
    configure_website_relation()


@when('config.changed')
def config_changed():
    config = hookenv.config()
    mirror_uri = config.get('mirror-uri')
    mirror_key = config.get('mirror-gpg-key')
    sign_key = config.get('sign-gpg-key')

    if mirror_uri and mirror_key and sign_key:
        mirror_fprint, sign_fprint = import_gpg_keys(mirror_key, sign_key)
        # XXX for now just log the imported keys
        hookenv.log(
            "import keys fingerprints {} {}".format(
                mirror_fprint, sign_fprint))


@when('static-website.available')
def static_website_relation(apache):
    domain = hookenv.unit_public_ip()
    config = get_website_relation_config(domain)
    apache.send_domain(config['domain'])
    apache.send_site_config(config['site_config'])
    apache.send_site_modules(config['site_modules'])
    apache.send_ports(config['ports'])
    apache.send_enabled()
