"""Utilities and objects for working with Debian mirrors."""

from collections import (
    Mapping,
    namedtuple,
)

import yaml


def from_config(keyring, mirrors, origin):
    """Return a list of mirrors as defined in the given config values.

    Raise a ValueError if config values are not valid.
    """
    try:
        entries = yaml.safe_load(mirrors)
    except Exception as err:
        raise ValueError('cannot YAML decode mirrors value: {}'.format(err))
    if not isinstance(entries, (list, tuple)):
        raise ValueError('mirrors value is not a list')
    results = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError('mirrors value is not a list of maps')
        try:
            debline = entry['deb-line']
            pubkey = entry['pub-key']
        except KeyError as err:
            raise ValueError('mirrors value is missing keys: {}'.format(err))
        try:
            url, suite, components = debline.split(' ', maxsplit=2)
        except (TypeError, ValueError):
            raise ValueError('invalid debline {!r}'.format(debline))
        try:
            key = keyring.import_key(pubkey)
        except Exception as err:
            raise ValueError(
                'cannot import GPG public key {!r}: {}'.format(pubkey, err))
        results.append(Mirror(
            url=url,
            suite=suite,
            components=components,
            key=key,
            archs=entry.get('archs', 'source i386 amd64'),
            version=entry.get('version', ''),
            origin=origin,
        ))
    return tuple(results)


# Mirror represents a debian mirror.
Mirror = namedtuple('Mirror', 'url suite components key archs version origin')
