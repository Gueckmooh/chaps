"Options module"
import argparse
import sys

from .verbosity import warn, err

VERSION = "%(VERSION)s"

ARGS = None


def _commasep_intlist(string):
    lst = string.split(",")
    ret = []
    for val in lst:
        try:
            ret += [int(val)]
        except ValueError:
            msg = "in '{}': '{}' is not an integer".format(string, val)
            raise argparse.ArgumentTypeError(msg)
    return ret


def _filetype(mode):
    def checker(string):
        try:
            f = open(string, mode)
            f.close()
        except FileNotFoundError:
            msg = "file {} not found".format(string)
            raise argparse.ArgumentTypeError(msg)
        return string

    return checker


def parse_args():
    parser = argparse.ArgumentParser(
        description="Cut audio/video file on chapters using ffmpeg."
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        type=_filetype("r"),
        help="The name of the input file.",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {}".format(VERSION),
    )

    parser.add_argument(
        "--restrict-filenames",
        action="store_true",
        dest="restrictfilenames",
        default=False,
        help="""Restrict filenames to only ASCII characters, and avoid "&"
        and spaces in filenames""",
    )

    parser.add_argument(
        "-o",
        "--output",
        action="store",
        default="%(title)s-%(chapter-title)s.%(ext)s",
        dest="outtmpl",
        metavar="TEMPLATE",
        help="""Output filename template, see the "OUTPUT TEMPLATE" for all
            the info. [Default: "%%(title)s-%%(chapter-title)s.%%(ext)s"]""",
    )

    parser.add_argument(
        "-c",
        "--copy",
        action="store_true",
        default=False,
        dest="codeccopy",
        help="Indicate to ffmpeg that the stream is not to be re-encoded.",
    )

    parser.add_argument(
        "-D",
        "--dry-run",
        action="store_true",
        default=False,
        dest="dryrun",
        help="Do not write anything to disk.",
    )

    parser.add_argument(
        "--only-chapters",
        action="store",
        default=None,
        dest="onlychapters",
        metavar="LIST",
        type=_commasep_intlist,
        help="""Indicate the chapters to extract, LIST is a comma separated
        integer list e.g., 1,2,5. This indicates to the program to extract only
        chapters 1, 2 and 5""",
    )

    parser.add_argument(
        "-p",
        "--print-chapters",
        action="store_true",
        default=False,
        dest="printchapters",
        help="Prints chapter list.",
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

    args = parser.parse_args()

    if args.quiet and args.verbose:
        warn("Warning, -q and -v are mutual exclusive arguments")
    elif not args.quiet and args.verbose is None:
        args.verbose = 1
    elif not args.quiet and args.verbose > 3:
        warn("Warning, no need to pass more than 3 v's")
        args.verbose = 3

    # if args.onlychapters:
    #     try:
    #         args.onlychapters = [int(x) for x in args.onlychapters.split(",")]
    #     except ValueError:
    #         err("--only-chapters option only accepts integer list")
    #         sys.exit(1)

    global ARGS
    ARGS = args

    return args


def get_args():
    return ARGS
