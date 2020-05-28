#!/usr/bin/env python

from __future__ import unicode_literals

# Allow direct execution
import os
import sys
import unittest
from unittest.mock import patch

from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chapter_split.util import yes_no_p


class TestJson(unittest.TestCase):
    def test_yes_no_p_yy(self):
        with patch("builtins.input", return_value="y"):
            self.assertEqual(yes_no_p("Test", "y"), True)

    def test_yes_no_p_yn(self):
        with patch("builtins.input", return_value="y"):
            self.assertEqual(yes_no_p("Test", "n"), True)

    def test_yes_no_p_ny(self):
        with patch("builtins.input", return_value="n"):
            self.assertEqual(yes_no_p("Test", "y"), False)

    def test_yes_no_p_nn(self):
        with patch("builtins.input", return_value="n"):
            self.assertEqual(yes_no_p("Test", "n"), False)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
