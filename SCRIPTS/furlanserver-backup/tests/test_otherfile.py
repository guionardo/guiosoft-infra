import unittest
import os
import logging
from src.other_files import OtherFile


class TestOtherFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG)
        return super().setUpClass()

    def test_otherfile_normal(self):
        otherfile = OtherFile('/etc/fstab')
        self.assertEqual('/etc/fstab', otherfile.filename)

    def test_otherfile_hostname(self):
        otherfile = OtherFile('{hostname}[hostname.txt]')
        self.assertTrue(os.path.isfile(otherfile.filename))
        del otherfile
