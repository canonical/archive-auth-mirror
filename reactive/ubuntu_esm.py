
from charms.reactive import (
    when,
    when_not,
    set_state,
)
from charms.reactive.decorators import hook
from charmhelpers.core import hookenv
from charmhelpers.fetch import apt_install

from charms.ubuntu_esm.utils import (
    configure_website_relation,
    install_resources,
)

from charms.ubuntu_esm.gpg import import_gpg_keys


PACKAGES = ['reprepro']


@when_not('ubuntu-esm.installed')
def install():
    apt_install(PACKAGES, fatal=True)
    install_resources()
    set_state('ubuntu-esm.installed')


@when('config.changed')
def config_changed():
    config = hookenv.config()
    service_url = config.get('service-url')
    mirror_uri = config.get('mirror-uri')
    mirror_key = config.get('mirror-gpg-key')
    sign_key = config.get('sign-gpg-key')

    configure_website_relation(domain=service_url)
    if mirror_uri and mirror_key and sign_key:
        mirror_fprint, sign_fprint = import_gpg_keys(mirror_key, sign_key)
        # XXX for now just log the imported keys
        hookenv.log(
            "import keys fingerprints {} {}".format(
                mirror_fprint, sign_fprint))


@hook('static-website-relation-{joined,changed}')
def website_relation():
    configure_website_relation()
