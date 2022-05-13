#!/usr/bin/env python

from __future__ import unicode_literals

# Allow direct execution
import os
import sys
import unittest
from unittest.mock import patch

from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chapter_split.util as util

comment_1 = """Cello collection of Studio ghibli with Calcifer in fireplace.
---------------------------------------------------------------------------------------------------------
[00:00:00] 千と千尋の神隠しメドレー     「千と千尋の神隠し」(Medley of "Spirited away")
[00:05:05] アドリアの海へ     「红の豚」("To Adriatic sea" from "Porco Roso")
[00:09:30] 君をのせて     「天空の城ラピュタ」("Carrying you" from "Laputa: Castle in the Sky ")
[00:13:03] 風の谷のナウシカ     「風の谷のナウシカ」(Theme of "Naushika of the valley of the wind")
[00:16:08] となりのトトロ     「となりのトトロ」(Theme of "My Neighbor Totoro")
[00:19:25] はにゅうの宿     「火垂るの墓」("Home, Sweet Home" from "Grave of the fireflies")
[00:22:20] さくらんぼの実る頃     「红の豚」( "The time of the cherries" from "Porco Roso")
[00:26:50] 風の通り道     「となりのトトロ」("Path of the wind" from "My Neighbor Totoro")
[00:30:22] やさしさに包まれたなら     「魔女の宅急便」("Being enclosed softly" from "Kiki's delivery service" )
[00:35:23] 世界の约束     「ハウルの動く城」("The promise of the world" from "Howl's moving castle")
[00:40:29] 天空の城ラピュタ     「天空の城ラピュタ」(Theme of "Laputa: Castle in the Sky" )
[00:44:35] ナウシカメドレー     「風の谷のナウシカ」(Medley of "Naushika of the valley of the wind")
[00:52:58] もののけ姫     「もののけ姫」(Theme of "Princess mononoke")
[00:57:49] いつも何度でも     「千と千尋の神隠し」("Always with me" from "Spirited away")
---------------------------------------------------------------------------------------------------------
This video is only for promotion.
Subscribe Koduck Weng for more BGM incoming!
#Ghibli #Cello"""  # noqa

com1_exp = [
    '[00:00:00] 千と千尋の神隠しメドレー     「千と千尋の神隠し」(Medley of "Spirited away")',  # noqa
    '[00:05:05] アドリアの海へ     「红の豚」("To Adriatic sea" from "Porco Roso")',
    '[00:09:30] 君をのせて     「天空の城ラピュタ」("Carrying you" from "Laputa: Castle in the Sky ")',  # noqa
    '[00:13:03] 風の谷のナウシカ     「風の谷のナウシカ」(Theme of "Naushika of the valley of the wind")',  # noqa
    '[00:16:08] となりのトトロ     「となりのトトロ」(Theme of "My Neighbor Totoro")',  # noqa
    '[00:19:25] はにゅうの宿     「火垂るの墓」("Home, Sweet Home" from "Grave of the fireflies")',  # noqa
    '[00:22:20] さくらんぼの実る頃     「红の豚」( "The time of the cherries" from "Porco Roso")',  # noqa
    '[00:26:50] 風の通り道     「となりのトトロ」("Path of the wind" from "My Neighbor Totoro")',  # noqa
    '[00:30:22] やさしさに包まれたなら     「魔女の宅急便」("Being enclosed softly" from "Kiki\'s delivery service" )',  # noqa
    '[00:35:23] 世界の约束     「ハウルの動く城」("The promise of the world" from "Howl\'s moving castle")',  # noqa
    '[00:40:29] 天空の城ラピュタ     「天空の城ラピュタ」(Theme of "Laputa: Castle in the Sky" )',  # noqa
    '[00:44:35] ナウシカメドレー     「風の谷のナウシカ」(Medley of "Naushika of the valley of the wind")',  # noqa
    '[00:52:58] もののけ姫     「もののけ姫」(Theme of "Princess mononoke")',  # noqa
    '[00:57:49] いつも何度でも     「千と千尋の神隠し」("Always with me" from "Spirited away")',  # noqa
]


def make_print_seq(seq):
    def make_generator(seq):
        for v in seq:
            yield v

    generator = make_generator(seq)

    def fake_ipt(_):
        return next(generator)

    def ret():
        return fake_ipt

    return ret


class TestJson(unittest.TestCase):
    def test_yes_no_p(self):
        with patch("builtins.input", return_value="y"):
            self.assertTrue(util.yes_no_p("Test", "y"))
        with patch("builtins.input", return_value="y"):
            self.assertTrue(util.yes_no_p("Test", "n"))
        with patch("builtins.input", return_value="n"):
            self.assertFalse(util.yes_no_p("Test", "y"))
        with patch("builtins.input", return_value="n"):
            self.assertFalse(util.yes_no_p("Test", "n"))
        with patch("builtins.input", return_value="y"):
            try:
                util.yes_no_p("Test", "o")
                self.assertFalse(True)
            except Exception:
                self.assertTrue(True)
        with patch(
            "builtins.input", new_callable=make_print_seq(["o", "v", "y"])
        ):
            self.assertTrue(util.yes_no_p("Test", "y"))

    def test_search_all(self):
        res = util.search_all(r"^.*(((\d|)\d:|)\d|)\d:\d\d.*$", comment_1)
        self.assertEqual(res, com1_exp)

    def test_search_iter(self):
        k = 0
        for v in util.search_iter(r"^.*(((\d|)\d:|)\d|)\d:\d\d.*$", comment_1):
            self.assertEqual(com1_exp[k], v)
            k += 1

    def test_sec_to_hour(self):
        self.assertEqual(util.sec_to_hour(2345), "00:39:05")
        self.assertEqual(util.sec_to_hour(3600), "01:00:00")
        self.assertEqual(util.sec_to_hour(1111), "00:18:31")
        self.assertEqual(util.sec_to_hour(123), "00:02:03")

    def test_msec_to_hour(self):
        self.assertEqual(util.msec_to_hour(15024918), "04:10:24.917")
        self.assertEqual(util.msec_to_hour(1524), "00:00:01.524")
        self.assertEqual(util.msec_to_hour(67546), "00:01:07.546")
        self.assertEqual(util.msec_to_hour(98479), "00:01:38.478")

    def test_sanitize_filename(self):
        ltest = [
            ("with spaces", "with_spaces"),
            ("with é", "with_e"),
            ("with ?", "with"),
            ('with "quotes"', "with_quotes"),
            ("with: colon", "with_-_colon"),
            ("with \\", "with"),
            ("with /", "with"),
            ("with |", "with"),
            ("with *", "with"),
            ("with <>", "with"),
            ("with てすつ", "with"),
            ("with 00:34:00", "with_00_34_00"),
            ("with   more     spaces", "with_more_spaces"),
            ("   with spaces   ", "with_spaces"),
            ("-_with_-", "with_-"),
            ("-with-", "_with-"),
            ("", "_"),
        ]
        for (filename, exp) in ltest:
            print(
                'Testing\
                util.sanitize_filename("{}", True)'.format(
                    filename
                )
            )
            self.assertEqual(util.sanitize_filename(filename, True), exp)

        ltest = [
            ("with spaces", "with_spaces"),
            ("with é", "with_e"),
            ("with ?", "with_"),
            ('with "quotes"', "with_quotes"),
            ("with: colon", "with_-_colon"),
            ("with \\", "with__"),
            ("with /", "with__"),
            ("with |", "with__"),
            ("with *", "with__"),
            ("with <>", "with___"),
            ("with てすつ", "with____"),
            ("with 00:34:00", "with_00_34_00"),
            ("with   more     spaces", "with___more_____spaces"),
            ("   with spaces   ", "___with_spaces___"),
            ("-_with_-", "-_with_-"),
            ("-with-", "-with-"),
            ("", ""),
        ]
        for (filename, exp) in ltest:
            print(
                'Testing \
                util.sanitize_filename("{}", True, is_id=True)'.format(
                    filename
                )
            )
            self.assertEqual(
                util.sanitize_filename(filename, True, is_id=True), exp
            )

        ltest = [
            ("with spaces", "with spaces"),
            ("with é", "with é"),
            ("with ?", "with "),
            ('with "quotes"', "with 'quotes'"),
            ("with: colon", "with - colon"),
            ("with \\", "with "),
            ("with /", "with "),
            ("with |", "with "),
            ("with *", "with "),
            ("with <>", "with "),
            ("with てすつ", "with てすつ"),
            ("with 00:34:00", "with 00_34_00"),
            ("with   more     spaces", "with   more     spaces"),
            ("   with spaces   ", "   with spaces   "),
            ("-_with_-", "__with_-"),
            ("-with-", "_with-"),
            ("", "_"),
        ]
        # for (filename, exp) in ltest:
        #     self.assertEqual(util.sanitize_filename(filename, False), exp)

        ltest = [
            ("with spaces", "with spaces"),
            ("with é", "with é"),
            ("with ?", "with "),
            ('with "quotes"', "with 'quotes'"),
            ("with: colon", "with - colon"),
            ("with \\", "with _"),
            ("with /", "with _"),
            ("with |", "with _"),
            ("with *", "with _"),
            ("with <>", "with __"),
            ("with てすつ", "with てすつ"),
            ("with 00:34:00", "with 00_34_00"),
            ("with   more     spaces", "with   more     spaces"),
            ("   with spaces   ", "   with spaces   "),
            ("-_with_-", "-_with_-"),
            ("-with-", "-with-"),
            ("", ""),
        ]
        for (filename, exp) in ltest:
            print(
                'Testing\
                util.sanitize_filename("{}", is_id=True)'.format(
                    filename
                )
            )
            self.assertEqual(util.sanitize_filename(filename, is_id=True), exp)

    def test_gen_filename(self):
        chapter = {
            "tags": {"title": "chapter-title"},
            "id": 340,
        }
        metadata = {"title": "media-title"}
        fmt = {"format_name": "mp3"}
        ltest = [
            (
                "%(chapter-id)s-%(chapter-title)s.%(ext)s",
                "340-chapter-title.mp3",
            ),
            (
                "%(chapter-index)s-%(chapter-title)s.%(ext)s",
                "341-chapter-title.mp3",
            ),
            (
                "%(title)s-%(chapter-index)s.%(chapter-title)s.%(ext)s",
                "media-title-341.chapter-title.mp3",
            ),
        ]
        for (template, exp) in ltest:
            print(
                'Testing\
                util.gen_filename("{}", chapter, metadata, fmt)'.format(
                    template
                )
            )
            self.assertEqual(
                util.gen_filename(template, chapter, metadata, fmt), exp
            )

    def test_gen_filename_no_title(self):
        chapter = {
            "tags": {"title": "chapter-title"},
            "id": 340,
        }
        metadata = {}
        fmt = {"filename": "test/media-title.mp3", "format_name": "mp3"}
        ltest = [
            (
                "%(chapter-id)s-%(chapter-title)s.%(ext)s",
                "340-chapter-title.mp3",
            ),
            (
                "%(chapter-index)s-%(chapter-title)s.%(ext)s",
                "341-chapter-title.mp3",
            ),
            (
                "%(title)s-%(chapter-index)s.%(chapter-title)s.%(ext)s",
                "media-title-341.chapter-title.mp3",
            ),
        ]
        for (template, exp) in ltest:
            print(
                'Testing\
                util.gen_filename("{}", chapter, metadata, fmt)'.format(
                    template
                )
            )
            self.assertEqual(
                util.gen_filename(template, chapter, metadata, fmt), exp
            )

    def test_get_filesystem_encoding(self):
        encoding = sys.getfilesystemencoding()
        self.assertEqual(util.get_filesystem_encoding(), encoding)

    def test_shell_quote(self):
        encoding = sys.getfilesystemencoding()
        ltest = [(["ffmpeg", "-o", "bla blip"], "ffmpeg -o 'bla blip'")]
        for args, exp in ltest:
            self.assertEqual(util.shell_quote(args), exp)
            self.assertEqual(
                util.shell_quote([x.encode(encoding) for x in args]), exp,
            )

    def test_parse_duration(self):
        ltest = [
            ("0.35", 0.35),
            ("42", 42.0),
            ("03:40", 220.0),
            ("1:35:44", 5744.0),
            ("4:3:2:1", 356521.0),
            ("42s", 42.0),
            ("42 sec", 42.0),
            ("42 second", 42.0),
            ("42seconds", 42.0),
            ("3m40s", 220.0),
            ("3min 40sec", 220.0),
            ("3minute40second", 220.0),
            ("3 minutes 40 s", 220.0),
            ("1h3m40s", 3820.0),
            ("1hour 3min 40sec", 3820.0),
            ("1 hours 3minute40second", 3820.0),
            ("3d T1h3m40s", 263020.0),
            ("3 day T1hour 3min 40sec", 263020.0),
            ("3daysT1 hours 3minute40second", 263020.0),
            ("1.30 hours", 4680.0),
            ("30.50mins", 1830.0),
            ("30.50 minutes", 1830.0),
            ("pouet", None),
            (None, None),
        ]
        for duration, exp in ltest:
            print(
                """Testing\
                util.parse_duration("{}")""".format(
                    duration
                )
            )
            self.assertEqual(util.parse_duration(duration), exp)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
