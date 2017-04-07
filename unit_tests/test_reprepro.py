import os
import logging
import tempfile
import textwrap
from pathlib import Path
from subprocess import CalledProcessError

from fixtures import TestWithFixtures, LoggerFixture

from archive_auth_mirror.reprepro import Reprepro


class RepreproTest(TestWithFixtures):

    def setUp(self):
        super().setUp()
        self.logger = self.useFixture(LoggerFixture(level=logging.DEBUG))

    def test_execute(self):
        """The execute function calls reprepro with the specified args."""
        reprepro = Reprepro(logging.getLogger(''), binary='/bin/echo')
        reprepro.execute('export', 'ubuntu')
        self.assertEqual(
            'running "/bin/echo --basedir /srv/archive-auth-mirror/reprepro'
            ' --confdir /srv/archive-auth-mirror/reprepro/conf'
            ' --outdir /srv/archive-auth-mirror/static/ubuntu'
            ' --gnupghome /srv/archive-auth-mirror/reprepro/.gnupg'
            ' export ubuntu"\n'
            # output from the process
            ' --basedir /srv/archive-auth-mirror/reprepro '
            '--confdir /srv/archive-auth-mirror/reprepro/conf '
            '--outdir /srv/archive-auth-mirror/static/ubuntu '
            '--gnupghome /srv/archive-auth-mirror/reprepro/.gnupg '
            'export ubuntu\n',
            self.logger.output)

    def test_execute_fail(self):
        """If the command fails, an exception is raised."""
        reprepro = Reprepro(logging.getLogger(''), binary='/bin/false')
        with self.assertRaises(CalledProcessError) as context_manager:
            reprepro.execute('export', 'ubuntu')
        self.assertEqual(1, context_manager.exception.returncode)
        self.assertEqual(
            ['/bin/false', '--basedir', '/srv/archive-auth-mirror/reprepro',
             '--confdir', '/srv/archive-auth-mirror/reprepro/conf',
             '--outdir', '/srv/archive-auth-mirror/static/ubuntu',
             '--gnupghome', '/srv/archive-auth-mirror/reprepro/.gnupg',
             'export', 'ubuntu'],
            context_manager.exception.cmd)

    def test_execute_log_error(self):
        """If the command fails, stderr is logged."""
        fd, name = tempfile.mkstemp()
        os.close(fd)
        binary = Path(name)
        self.addCleanup(binary.unlink)
        binary.write_text(
            textwrap.dedent(
                '''#!/bin/sh
                echo fail >&2
                exit 1
                '''))
        binary.chmod(0o700)

        reprepro = Reprepro(logging.getLogger(''), binary=str(binary))
        with self.assertRaises(CalledProcessError):
            reprepro.execute('export', 'ubuntu')
        self.assertIn('fail\n', self.logger.output)
