from charms.reactive import when_not, set_state


@when_not('ubuntu-esm.installed')
def install_ubuntu_esm():
    set_state('ubuntu-esm.installed')
