import logging
from unittest import TestCase

from src.shell import run_shell


class TestShell(TestCase):
    def test_run_shell_should_success(self):
        output, success = run_shell("ls -la")
        self.assertTrue(success)

    def test_run_shell_should_fail(self):
        logger = logging.getLogger("shell")
        with self.assertLogs(logger, logging.ERROR):
            output, success = run_shell("bad_command")
            self.assertTrue(success)
