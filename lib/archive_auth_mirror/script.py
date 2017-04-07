"""Common setup functions for scripts."""

import os
import sys
import logging
from logging.handlers import SysLogHandler

import yaml


def setup_logger(level=logging.DEBUG, echo=False):
    """Setup and return the logger for the script.

    If echo is True, logging is also written to stderr.
    """
    name = os.path.basename(sys.argv[0])
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(
        SysLogHandler(address='/dev/log', facility=SysLogHandler.LOG_DAEMON))
    if echo:
        logger.addHandler(logging.StreamHandler())
    return logger


def get_config(config_file):
    """Return the config or None if no file is found."""
    if not config_file.exists():
        return
    with config_file.open() as fh:
        return yaml.load(fh)
