"Options module"
import argparse

from .verbosity import warn

VERSION = "%(VERSION)s"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Cut audio/video file on chapters using ffmpeg."
    )
    parser.add_argument(
        "file", metavar="FILE", type=str, help="The name of the input file.",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {}".format(VERSION),
    )

    verbosity = parser.add_argument_group("verbosity")

    verbosity.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbose",
        help="""Makes the program more talkative, duplicate for more verbosity
            (e.g., -vvv).""",
    )

    verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        dest="quiet",
        default=False,
        help="Makes the program quiet.",
    )

    verbosity.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help="Print debug infos.",
    )

    _args = parser.parse_args()

    if _args.quiet and _args.verbose:
        warn("Warning, -q and -v are mutual exclusive arguments")
    elif not _args.quiet and _args.verbose is None:
        _args.verbose = 1
    elif not _args.quiet and _args.verbose > 3:
        warn("Warning, no need to pass more than 3 v's")
        _args.verbose = 3

    return _args
