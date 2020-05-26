#!/usr/bin/env python

from __future__ import unicode_literals

# Allow direct execution
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chapter_split as chaps


class TestJson(unittest.TestCase):
    def test_from_json(self):
        jchap = [
            {
                "id": 0,
                "time_base": "1/1000",
                "start": 0,
                "start_time": "0.000000",
                "end": 305000,
                "end_time": "305.000000",
                "tags": {"title": "chap1"},
            },
            {
                "id": 1,
                "time_base": "1/1000",
                "start": 305000,
                "start_time": "305.000000",
                "end": 570000,
                "end_time": "570.000000",
                "tags": {"title": "chap2"},
            },
            {
                "id": 2,
                "time_base": "1/1000",
                "start": 570000,
                "start_time": "570.000000",
                "end": 783000,
                "end_time": "783.000000",
                "tags": {"title": "chap3"},
            },
        ]
        exp_chap = [
            {"start": "00:00:00", "end": "00:05:05", "title": "chap1"},
            {"start": "00:05:05", "end": "00:09:30", "title": "chap2"},
            {"start": "00:09:30", "end": "00:13:03", "title": "chap3"},
        ]
        chap = chaps.parse_chapters(jchap)
        self.assertEqual(chap, exp_chap)

    def test_to_json(self):
        file = "{}/sample_files/empty.mp3".format(
            os.path.dirname(os.path.abspath(__file__))
        )
        exp = [
            {
                "id": 0,
                "time_base": "1/1000",
                "start": 0,
                "start_time": "0.000000",
                "end": 10000,
                "end_time": "10.000000",
                "tags": {"title": "chapter #1"},
            },
            {
                "id": 1,
                "time_base": "1/1000",
                "start": 10000,
                "start_time": "10.000000",
                "end": 20000,
                "end_time": "20.000000",
                "tags": {"title": "chapter #2"},
            },
            {
                "id": 2,
                "time_base": "1/1000",
                "start": 20000,
                "start_time": "20.000000",
                "end": 30000,
                "end_time": "30.000000",
                "tags": {"title": "chapter #3"},
            },
        ]
        val = chaps.get_chapters(file)
        self.assertEqual(val, exp)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
