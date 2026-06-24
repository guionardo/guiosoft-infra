import unittest

from src.byte_str import _process_comma, parse_bytes


class TestByteStr(unittest.TestCase):
    def test_process_comma(self):
        for origin, fixed in [("0.10", "0.10"), ("100,230.231", "100230.231")]:
            processed = _process_comma(origin)
            self.assertEqual(processed, fixed)

    def test_parse_bytes(self):
        for origin, result in [
            ("647", 647),
            ("1.2K", 1228),
            ("5.3M", 5557452),
            ("32,123.1G", 34491915986534),
        ]:
            processed = parse_bytes(origin)
            self.assertEqual(
                processed, result, f"Expected {origin} = {result} -> got {processed}"
            )
