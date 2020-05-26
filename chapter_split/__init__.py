#!/usr/bin/env python3

from .options import parse_args

from .verbosity import (
    vprint,
    vvprint,
    vvvprint,
    set_level as verbosity_set_level,
    VERBOSE_LEVEL,
    VVERBOSE_LEVEL,
    VVVERBOSE_LEVEL,
)

from .ffmpeg import get_chapters

from .util import sec_to_hour

# re.findall ("('.*'|\".*\"|\S+)", s)

# ffprobe -i f -print_format json -show_chapters -loglevel error


def parse_chapters(chapters):
    chaps = []
    for chapter in chapters:
        chaps += [
            {
                "start": "{}".format(
                    sec_to_hour(int(chapter["start"]) / 1000)
                ),
                "end": "{}".format(sec_to_hour(int(chapter["end"]) / 1000)),
                "title": chapter["tags"]["title"],
            }
        ]
    return chaps


def main():
    args = parse_args()
    # Setup the verbose functions
    v = args.verbose
    if v == 1:
        verbosity_set_level(VERBOSE_LEVEL, debug=args.debug)
    elif v == 2:
        verbosity_set_level(VVERBOSE_LEVEL, debug=args.debug)
    elif v == 3:
        verbosity_set_level(VVVERBOSE_LEVEL, debug=args.debug)
    vvprint("Given file is {}".format(args.file))
    chapters = get_chapters(args.file)
    chapters = parse_chapters(chapters)
    vvvprint(chapters)


if __name__ == "__main__":
    main()
