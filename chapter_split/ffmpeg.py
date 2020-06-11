"""FFMPEG module"""

import json
import subprocess as sp
import sys
import math
import os

from .verbosity import vprint, vvprint, vvvprint, err


from .util import (
    sanitize_filename,
    gen_filename,
    msec_to_hour,
    sec_to_hour,
    shell_quote,
    parse_duration,
)

from .progress import Progress, Line, Placeholder


from .options import get_args


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
    j = get_infos(filename)
    vprint("[chaps] Extract chapters from json infos...")
    chapters = j["chapters"]
    vvprint("Found {:d} chapters".format(len(chapters)))
    return chapters


def get_chapter_from_json(jinfos):
    vprint("[chaps] Extract chapters from json infos...")
    chapters = jinfos["chapters"]
    vvprint("Found {:d} chapters".format(len(chapters)))
    return chapters


def get_metadatas(filename):
    j = get_infos(filename)
    vprint("[chaps] Extract metadata from json infos...")
    metadatas = j["format"]["tags"]
    return metadatas


def get_metadatas_from_json(jinfos):
    vprint("[chaps] Extract metadata from json infos...")
    metadatas = jinfos["format"]["tags"]
    return metadatas


def get_format(filename):
    j = get_infos(filename)
    vprint("[chaps] Extract format informations from json infos...")
    fmt = j["format"]
    return fmt


def get_format_from_json(jinfos):
    vprint("[chaps] Extract format informations from json infos...")
    fmt = jinfos["format"]
    return fmt


def run_ffmpeg(
    input_path,
    out_path,
    opts,
    dry=False,
    progress=False,
    duration=None,
    line=None,
    bar=None,
    percentmsg=None,
):
    cmd = ["ffmpeg", "-y", "-i", input_path]
    cmd += opts
    cmd += ["-loglevel", "repeat+info", "-progress", "/dev/stdout"]
    cmd += [out_path]

    vvprint("[debug] ffmpeg command line: {}".format(shell_quote(cmd)))

    if not dry:
        p = sp.Popen(
            cmd,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            stdin=sp.PIPE,
            universal_newlines=True,
        )
        if progress:
            if bar:
                bar.set_percent(0)
                percentmsg.set_value(" (  0%)\r")
            sys.stdout.write("{}\r".format(line))
            while True:
                try:
                    stdout, stderr = p.communicate(timeout=1)
                    if bar:
                        bar.set_percent(100)
                        percentmsg.set_value(" (100%)")
                    sys.stdout.write("{}\r".format(line))
                    break
                except sp.TimeoutExpired:
                    while True:
                        p.stdout.flush()
                        li = p.stdout.readline().strip()
                        if "out_time=" in li[:9]:
                            current_duration = parse_duration(li.split("=")[1])
                            percentage = math.floor(
                                (current_duration / duration) * 100
                            )
                            bar.set_percent(percentage)
                            percentmsg.set_value(
                                " ({: 3d}%)".format(percentage)
                            )
                            sys.stdout.write("{}\r".format(line))
                            break
        else:
            stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode("utf-8", "replace")
            err(stderr.strip().split("\n")[-1])
            sys.exit(1)


def split_file_on_chapters(filename, jinfos, chapters=None):
    if chapters is None:
        chapters = get_chapter_from_json(jinfos)
    metadata = get_metadatas_from_json(jinfos)
    fmt = get_format_from_json(jinfos)
    args = get_args()
    sanitize = lambda v: sanitize_filename(v, args.restrictfilenames)
    nb_chaps = len(args.onlychapters) if args.onlychapters else len(chapters)
    i = 1

    line = None
    # Setup progress bar
    if args.progress:
        if not args.codeccopy:
            width, _ = os.get_terminal_size()
            pchapmsg = "Chapter {0:{1}}/{2} ".format(
                i, len(str(nb_chaps)), nb_chaps
            )
            pchap = Placeholder(len(pchapmsg), value=pchapmsg)
            pprcntmsg = " (  0%)"
            pprcnt = Placeholder(len(pprcntmsg), value=pprcntmsg)
            progress1_width = math.floor(
                (width - len(pchapmsg) - len(pprcntmsg) - len(": Progress "))
                / 2
            )
            progress1 = Progress(progress1_width)
            progress2_width = math.ceil(
                width
                - len(pchapmsg)
                - len(pprcntmsg)
                - len(": Progress ")
                - progress1_width
            )
            progress2 = Progress(progress2_width)
            line = Line(pchap, progress1, ": Progress ", progress2, pprcnt)
        else:
            width, _ = os.get_terminal_size()
            pchapmsg = "Chapter {0:{1}}/{2} ".format(
                i, len(str(nb_chaps)), nb_chaps
            )
            pchap = Placeholder(len(pchapmsg), value=pchapmsg)
            progress_width = math.floor((width - len(pchapmsg)))
            progress1 = Progress(progress_width)
            line = Line(pchap, progress1)
            progress2 = None
            pprcnt = None
    else:
        progress2 = None
        pprcnt = None

    for chap in chapters:
        if args.onlychapters and (chap["id"] + 1) not in args.onlychapters:
            continue
        if args.progress:
            pchap.set_value(
                "Chapter {0:{1}}/{2} ".format(i, len(str(nb_chaps)), nb_chaps)
            )
            progress1.set_percent(math.floor((i / nb_chaps) * 100))
        i += 1
        outfile = gen_filename(args.outtmpl, chap, metadata, fmt)
        outfile = sanitize(outfile)
        start = msec_to_hour(int(chap["start"]))
        end = msec_to_hour(int(chap["end"]))
        duration = float(chap["end_time"]) - float(chap["start_time"])
        command = [
            "-ss",
            start,
            "-to",
            end,
        ]
        if args.codeccopy:
            command += ["-codec", "copy"]

        run_ffmpeg(
            filename,
            outfile,
            command,
            dry=args.dryrun,
            duration=duration,
            progress=args.progress,
            line=line,
            bar=progress2,
            percentmsg=pprcnt,
        )
    if args.progress:
        sys.stdout.write("{}\n".format(line))


def print_chapters(filename, jinfos):
    chapters = get_chapter_from_json(jinfos)
    args = get_args()
    first = True
    for chap in chapters:
        if args.onlychapters and (chap["id"] + 1) not in args.onlychapters:
            continue
        if not first:
            print()
        else:
            first = False
        title = chap["tags"]["title"]
        id = chap["id"]
        index = chap["id"] + 1
        start = sec_to_hour(int(chap["start"]) / 1000)
        end = sec_to_hour(int(chap["end"]) / 1000)
        print("Title: {}".format(title))
        print("id: {}, index: {}".format(id, index))
        print("[{} - {}]".format(start, end))
