"""Cron job configuration."""

import textwrap

from .utils import get_paths


CRONTAB_TEMPLATE = textwrap.dedent(
    '''
    #  m h dom mon dow user  command
    */15 *   *   *   * root  {paths[bin]}/mirror-archive
    ''')


def install_crontab(paths=None):
    """Install the crontab file to periodically run the job."""
    if paths is None:
        paths = get_paths()

    with paths['cron'].open('w') as fh:
        fh.write(CRONTAB_TEMPLATE.format(paths=paths))


def remove_crontab(paths=None):
    """Remove the crontab file for the job."""
    if paths is None:
        paths = get_paths()

    cron_file = paths['cron']
    if cron_file.exists():
        cron_file.unlink()
