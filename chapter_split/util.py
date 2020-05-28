"""Utility module"""
import math
import re
import itertools
import sys
from shlex import quote

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
