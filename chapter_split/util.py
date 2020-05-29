"""Utility module"""
import math
import re
import itertools
import sys
from shlex import quote


def search_all(pat, content):
    reg = re.compile(pat, re.MULTILINE)
    found = []
    b = 0
    while True:
        matched = reg.search(content, b)
        if matched is None:
            break
        b = matched.end(0)
        found += [matched.group(0)]
    return found


def search_iter(pat, content):
    reg = re.compile(pat, re.MULTILINE)
    b = 0
    while True:
        matched = reg.search(content, b)
        if matched is None:
            break
        b = matched.end(0)
        yield matched.group(0)


ACCENT_CHARS = dict(
    zip(
        "ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñòóôõöőøœùúûüűýþÿ",
        itertools.chain(
            "AAAAAA",
            ["AE"],
            "CEEEEIIIIDNOOOOOOO",
            ["OE"],
            "UUUUUY",
            ["TH", "ss"],
            "aaaaaa",
            ["ae"],
            "ceeeeiiiionooooooo",
            ["oe"],
            "uuuuuy",
            ["th"],
            "y",
        ),
    )
)


def sec_to_hour(SEC):
    SEC = math.floor(SEC)
    MIN = math.floor(SEC / 60)
    HOUR = math.floor(MIN / 60)
    MIN = MIN % 60
    SEC = SEC % 60
    return "{:02d}:{:02d}:{:02d}".format(HOUR, MIN, SEC)


def msec_to_hour(MSEC):
    SEC = MSEC / 1000
    MIN = math.floor(math.floor(SEC) / 60)
    HOUR = math.floor(MIN / 60)
    MIN = MIN % 60
    SEC = SEC % 60
    PSEC = math.floor(SEC)
    PMSEC = math.floor((SEC - PSEC) * 1000)
    return "{:02d}:{:02d}:{:02d}.{:d}".format(HOUR, MIN, PSEC, PMSEC)


def sanitize_filename(s, restricted=False, is_id=False):
    """Sanitizes a string so it could be used as part of a filename.
    If restricted is set, use a stricter subset of allowed characters.
    Set is_id if this is not an arbitrary string, but an ID that should be kept
    if possible.
    """

    def replace_insane(char):
        if restricted and char in ACCENT_CHARS:
            return ACCENT_CHARS[char]
        if char == "?" or ord(char) < 32 or ord(char) == 127:
            return ""
        elif char == '"':
            return "" if restricted else "'"
        elif char == ":":
            return "_-" if restricted else " -"
        elif char in "\\/|*<>":
            return "_"
        if restricted and (char in "!&'()[]{}$;`^,#" or char.isspace()):
            return "_"
        if restricted and ord(char) > 127:
            return "_"
        return char

    # Handle timestamps
    s = re.sub(
        r"[0-9]+(?::[0-9]+)+", lambda m: m.group(0).replace(":", "_"), s
    )
    result = "".join(map(replace_insane, s))
    if not is_id:
        while "__" in result:
            result = result.replace("__", "_")
        result = result.strip("_")
        # Common case of "Foreign band name - English song title"
        if restricted and result.startswith("-_"):
            result = result[2:]
        if result.startswith("-"):
            result = "_" + result[len("-") :]
        result = result.lstrip(".")
        if not result:
            result = "_"
    return result


def gen_filename(template, chapter, metadata, fmt):
    filename = template
    filename = filename.replace("%(chapter-title)s", chapter["tags"]["title"])
    filename = filename.replace("%(chapter-id)s", str(chapter["id"]))
    filename = filename.replace("%(chapter-index)s", str(chapter["id"] + 1))
    filename = filename.replace("%(title)s", metadata["title"])
    filename = filename.replace("%(ext)s", fmt["format_name"])
    return filename


def get_filesystem_encoding():
    encoding = sys.getfilesystemencoding()
    return encoding if encoding is not None else "utf-8"


def shell_quote(args):
    quoted_args = []
    encoding = get_filesystem_encoding()
    for a in args:
        if isinstance(a, bytes):
            # We may get a filename encoded with 'encodeFilename'
            a = a.decode(encoding)
        quoted_args.append(quote(a))
    return " ".join(quoted_args)


def yes_no_p(message, default="N"):
    if default not in ["Y", "N", "y", "n"]:
        raise Exception("Wrong parameter in yes_no_p")
    yn = "[Y/n]" if default in ["Y", "y"] else "[y/N]"
    yes = ["Y", "y", ""] if default in ["Y", "y"] else ["Y", "y"]
    no = ["N", "n", ""] if default in ["N", "n"] else ["N", "n"]
    message += " " + yn + " "
    while True:
        ret = input(message)
        if ret in yes:
            return True
        elif ret in no:
            return False


def parse_duration(s):
    if not isinstance(s, str):
        return None

    s = s.strip()

    days, hours, mins, secs, ms = [None] * 5
    m = re.match(
        r"(?:(?:(?:(?P<days>[0-9]+):)?(?P<hours>[0-9]+):)?(?P<mins>[0-9]+):)?(?P<secs>[0-9]+)(?P<ms>\.[0-9]+)?Z?$",  # noqa
        s,
    )
    if m:
        days, hours, mins, secs, ms = m.groups()
    else:
        m = re.match(
            r"""(?ix)(?:P?
                (?:
                    [0-9]+\s*y(?:ears?)?\s*
                )?
                (?:
                    [0-9]+\s*m(?:onths?)?\s*
                )?
                (?:
                    [0-9]+\s*w(?:eeks?)?\s*
                )?
                (?:
                    (?P<days>[0-9]+)\s*d(?:ays?)?\s*
                )?
                T)?
                (?:
                    (?P<hours>[0-9]+)\s*h(?:ours?)?\s*
                )?
                (?:
                    (?P<mins>[0-9]+)\s*m(?:in(?:ute)?s?)?\s*
                )?
                (?:
                    (?P<secs>[0-9]+)(?P<ms>\.[0-9]+)?\s*s(?:ec(?:ond)?s?)?\s*
                )?Z?$""",
            s,
        )
        if m:
            days, hours, mins, secs, ms = m.groups()
        else:
            m = re.match(
                r"(?i)(?:(?P<hours>[0-9.]+)\s*(?:hours?)|(?P<mins>[0-9.]+)\s*(?:mins?\.?|minutes?)\s*)Z?$",  # noqa
                s,
            )
            if m:
                hours, mins = m.groups()
            else:
                return None

    duration = 0
    if secs:
        duration += float(secs)
    if mins:
        duration += float(mins) * 60
    if hours:
        duration += float(hours) * 60 * 60
    if days:
        duration += float(days) * 24 * 60 * 60
    if ms:
        duration += float(ms)
    return duration


def extract_chapters_txt(description, duration):
    if not description:
        return None
    chapter_lines = search_all(r"^.*(((\d|)\d:|)\d|)\d:\d\d.*$", description,)
    if not chapter_lines:
        return None
    for idx, chap in enumerate(chapter_lines):
        time_point = re.search(r"(((\d|)\d:|)\d|)\d:\d\d", chap).group(0)
        chap_name = re.sub(r"(((\d|)\d:|)\d|)\d:\d\d", "", chap)
        chapter_lines[idx] = (chap_name, time_point)
    chapters = []
    for next_num, (chapter_line, time_point) in enumerate(
        chapter_lines, start=1
    ):
        start_time = parse_duration(time_point)
        if start_time is None:
            continue
        if start_time > duration:
            break
        end_time = (
            duration
            if next_num == len(chapter_lines)
            else parse_duration(chapter_lines[next_num][1])
        )
        if end_time is None:
            continue
        if end_time > duration:
            end_time = duration
        if start_time > end_time:
            break
        chapter_title = re.sub(r"<a[^>]+>[^<]+</a>", "", chapter_line).strip(
            " \t-"
        )
        chapter_title = re.sub(r"\s+", " ", chapter_title)
        chapters.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "title": chapter_title,
            }
        )
    return chapters
