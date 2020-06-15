#!/usr/bin/env python3

import sys

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

from . import ffmpeg

from .util import sec_to_hour, extract_chapters_txt


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
    if args.chapter_file:
        infos = ffmpeg.get_infos(args.file)
        duration = float(infos["format"]["duration"])

        with open(args.chapter_file) as f:
            text = f.read()
            chapters = extract_chapters_txt(text, duration)
            ffmpeg.split_file_on_chapters(
                args.file, ffmpeg.get_infos(args.file), chapters=chapters
            )
        sys.exit(0)
    if args.printchapters:
        ffmpeg.print_chapters(args.file, ffmpeg.get_infos(args.file))
        sys.exit(0)
    ffmpeg.split_file_on_chapters(args.file, ffmpeg.get_infos(args.file))


if __name__ == "__main__":
    main()
