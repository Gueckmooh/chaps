"""FFMPEG module"""

import json
import subprocess as sp


from .verbosity import (
    vprint,
    vvprint,
    vvvprint,
)


def get_chapters(filename):
    vprint("[ffprobe] get chapters...")
    command = [
        "ffprobe",
        "-i",
        filename,
        "-print_format",
        "json",
        "-show_chapters",
        "-loglevel",
        "error",
    ]
    vvprint("Command is {}".format(" ".join(command)))
    output = sp.check_output(command)
    j = json.loads(output)
    chapters = j["chapters"]
    vvprint("Found {:d} chapters".format(len(chapters)))
    return chapters
