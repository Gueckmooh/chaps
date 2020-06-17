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

from .status import Status, Progress, Text

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
    input_path, out_path, opts, duration=None, status=None,
):
    args = get_args()
    cmd = ["ffmpeg", "-y", "-i", input_path]
    cmd += opts
    cmd += ["-loglevel", "repeat+info", "-progress", "/dev/stdout"]
    cmd += [out_path]

    vvprint("[debug] ffmpeg command line: {}".format(shell_quote(cmd)))

    if not args.dryrun:
        p = sp.Popen(
            cmd,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            stdin=sp.PIPE,
            universal_newlines=True,
        )
        if status:
            while True:
                try:
                    stdout, stderr = p.communicate(timeout=1)
                    if not args.codeccopy:
                        status.current_progress.set_value(1)
                    sys.stdout.write("{}\r".format(status))
                    break
                except sp.TimeoutExpired:
                    while True:
                        p.stdout.flush()
                        li = p.stdout.readline().strip()
                        if "out_time=" in li[:9]:
                            current_duration = parse_duration(li.split("=")[1])
                            percentage = current_duration / duration
                            status.current_progress.set_value(percentage)
                            sys.stdout.write("{}\r".format(status))
                            break
        else:
            stdout, stderr = p.communicate()
        if p.returncode != 0:
            stderr = stderr.decode("utf-8", "replace")
            err(stderr.strip().split("\n")[-1])
            sys.exit(1)


def make_status_bar(chapters):
    args = get_args()
    nb_chaps = len(chapters)
    s = None
    if args.progress:
        p1 = Text(name="chapters")
        p1.set_fmt(
            "Chapter {{chap:{0}d}}/{1}".format(len(str(nb_chaps)), nb_chaps),
            chap=0,
        )
        p2 = Progress(name="chapters_progress")
        p3 = Text(name="chapters_percent")
        s = Status(separator=" ", dynamic_width=True)
        if not args.codeccopy:
            p3.set_fmt("({value:3d}%): Progress", value=0)
            p4 = Progress(name="current_progress")
            s = s + p1 + p2 + p3 + p4
            return s
        else:
            p3.set_fmt("({value:3d}%)", value=0)
            s = s + p1 + p2 + p3
    return s


def extract_chapter(chap, metadata, fmt, filename, cur=0, tot=0, status=None):
    args = get_args()
    vprint(
        '\033[K[chaps] Extracting chapter "{}"...'.format(
            chap["tags"]["title"]
        )
    )
    sanitize = lambda v: sanitize_filename(v, args.restrictfilenames)
    if args.progress:
        status.chapters.chap = cur
        status.chapters_progress.set_value((cur - 1) / tot)
        status.chapters_percent.value = math.ceil((cur - 1) / tot * 100)
        sys.stdout.write("{}\r".format(status))
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
        filename, outfile, command, duration=duration, status=status,
    )


def split_file_on_chapters(filename, jinfos, chapters=None):
    if chapters is None:
        chapters = get_chapter_from_json(jinfos)
    metadata = get_metadatas_from_json(jinfos)
    fmt = get_format_from_json(jinfos)
    args = get_args()
    nb_chaps = len(args.onlychapters) if args.onlychapters else len(chapters)

    oc = args.onlychapters
    working_chapters = [
        chap
        for chap in chapters
        if (oc and ((chap["id"] + 1) in oc)) or oc is None
    ]

    # Setup progress bar
    status = make_status_bar(working_chapters)

    for i, chap in enumerate(working_chapters, start=1):
        extract_chapter(
            chap, metadata, fmt, filename, i, nb_chaps, status=status
        )
    if args.progress:
        status.chapters_progress.set_value(1)
        status.chapters_percent.value = 100
        sys.stdout.write("{}\n".format(status))


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
