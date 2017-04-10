import os
import sys
import logging
from logging.handlers import SysLogHandler

import yaml


def setup_logger(name=None):
    """Setup and return the logger for the script."""
    if not name:
        name = os.path.basename(sys.argv[0])

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(SysLogHandler())
    return logger


def get_config(config_file):
    """Return the config or None if no file is found."""
    if not config_file.exists():
        return
    with config_file.open() as fh:
        return yaml.load(fh)
