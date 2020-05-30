#!/usr/bin/env python

from __future__ import unicode_literals

# Allow direct execution
import os
import sys
import unittest
from unittest.mock import patch
import logging

from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chapter_split.verbosity import (
    vprint,
    vvprint,
    vvvprint,
    set_level as verbosity_set_level,
    VERBOSE_LEVEL,
    VVERBOSE_LEVEL,
    VVVERBOSE_LEVEL,
    ch,
)

logger = logging.getLogger("logger")
logger.removeHandler(ch)
print(logger.hasHandlers())
stream = StringIO()
stream_handler = logging.StreamHandler(stream)
logger.addHandler(stream_handler)


class TestJson(unittest.TestCase):
    def test_print(self):
        vprint("vprint")
        vvprint("vvprint")
        vvvprint("vvvprint")
        self.assertEqual(stream.getvalue(), "")

    def test_vprint(self):
        stream = StringIO()
        stream_handler.stream = stream
        verbosity_set_level(VERBOSE_LEVEL)
        vprint("vprint")
        vvprint("vvprint")
        vvvprint("vvvprint")
        self.assertEqual(stream.getvalue(), "vprint\n")

    def test_vvprint(self):
        stream = StringIO()
        stream_handler.stream = stream
        verbosity_set_level(VVERBOSE_LEVEL)
        vprint("vprint")
        vvprint("vvprint")
        vvvprint("vvvprint")
        self.assertEqual(stream.getvalue(), "vprint\nvvprint\n")

    def test_vvvprint(self):
        stream = StringIO()
        stream_handler.stream = stream
        verbosity_set_level(VVVERBOSE_LEVEL)
        vprint("vprint")
        vvprint("vvprint")
        vvvprint("vvvprint")
        self.assertEqual(stream.getvalue(), "vprint\nvvprint\nvvvprint\n")

    def test_vprint_debug(self):
        stream = StringIO()
        stream_handler.stream = stream
        verbosity_set_level(VERBOSE_LEVEL, debug=True)
        vprint("vprint")
        vvprint("vvprint")
        vvvprint("vvvprint")
        self.assertEqual(stream.getvalue(), "vprint\nvvprint\nvvvprint\n")


def main():
    unittest.main()


if __name__ == "__main__":
    main()
