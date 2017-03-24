#!/usr/bin/env python3

import sys
sys.path.append('lib')

from charms.layer import basic
basic.bootstrap_charm_deps()
basic.init_config_states()

from charms.reactive import main
main()
