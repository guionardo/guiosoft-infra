from datetime import timedelta
from time import time
from unittest import TestCase

from src.wait_uptime import wait_until_uptime


class TestWaitUntilUptime(TestCase):
    def test_wait(self):
        def wup(*args):
            return 0, "up 0 minutes"

        start_time = time()
        wait_until_uptime(timedelta(seconds=5), wup)
        elapsed_time = time() - start_time
        self.assertGreaterEqual(elapsed_time, 5)
        self.assertLessEqual(elapsed_time, 6)
