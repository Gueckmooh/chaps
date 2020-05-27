"""FFMPEG module"""

import json
import subprocess as sp


from .verbosity import (
    vprint,
    vvprint,
    vvvprint,
)


def get_infos(filename):
    vprint("[chaps] Getting infos from file...")
    vprint("[ffprobe] Getting json infos...")
    command = [
        "ffprobe",
        "-i",
        filename,
        "-print_format",
        "json",
        "-show_chapters",
        "-show_format",
        "-loglevel",
        "error",
    ]
    vvprint("Command is {}".format(" ".join(command)))
    output = sp.check_output(command)
    return json.loads(output)


def get_chapters(filename):
    vprint("[chaps] Extract chapters from json infos...")
    j = get_infos(filename)
    chapters = j["chapters"]
    vvprint("Found {:d} chapters".format(len(chapters)))
    return chapters
