"""Wrapper around the reprepro tool."""

from subprocess import Popen, PIPE, CalledProcessError

from .utils import get_paths


class Reprepro:
    """Wrapper to execute reprepro commands."""

    def __init__(self, logger, binary='/usr/bin/reprepro'):
        self._logger = logger
        self._binary = binary

    def execute(self, *args):
        """Execute the specified reprepro command."""
        command = self._get_command(args)

        self._logger.debug('running "{}"'.format(' '.join(command)))
        with Popen(command, stdout=PIPE, stderr=PIPE) as process:
            for line in iter(process.stdout.readline, b''):
                self._logger.info(' ' + line.strip().decode('utf8'))

            return_code = process.wait()
            if return_code:
                for line in process.stderr.readlines():
                    self._logger.error(' ' + line.strip().decode('utf8'))
                raise CalledProcessError(return_code, command)

    def _get_command(self, args):
        paths = get_paths()
        command = [
            self._binary,
            '--basedir', str(paths['reprepro']),
            '--confdir', str(paths['reprepro-conf']),
            '--outdir', str(paths['static'] / 'ubuntu'),
            '--gnupghome', str(paths['gnupghome'])]
        command.extend(args)
        return command
