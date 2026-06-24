import logging
import unittest

from src.pre_run_script import PreRunScript


class TestPreRunScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG)
        return super().setUpClass()

    def test_nolabel_script(self):
        prs = PreRunScript("ls")
        self.assertEqual("ls", prs.label)
        self.assertEqual("ls", prs.command)

    def test_labeled_script(self):
        prs = PreRunScript("[list files]ls")
        self.assertEqual("ls", prs.command)
        self.assertEqual("list files", prs.label)
