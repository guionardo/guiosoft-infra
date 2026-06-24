import datetime
import logging
import unittest

from src.lockfile import Lockfile


class TestLockFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG)
        return super().setUpClass()

    def test_lock(self):
        with Lockfile("test.lock", datetime.timedelta(seconds=30)) as lock:
            self.assertTrue(lock.is_locked)

            with Lockfile("test.lock", datetime.timedelta(seconds=2)) as lock2:
                self.assertFalse(lock2.is_locked)
