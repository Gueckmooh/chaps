"""FFMPEG module"""

import json
import subprocess as sp

from .verbosity import (
    vprint,
    vvprint,
    vvvprint,
)


from .util import *


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


def split_file_on_chapters(filename, jinfos):
    chapters = get_chapter_from_json(jinfos)
    metadata = get_metadatas_from_json(jinfos)
    fmt = get_format_from_json(jinfos)
    args = get_args()
    sanitize = lambda v: sanitize_filename(v, args.restrictfilenames)
    for chap in chapters:
        if args.onlychapters and (chap["id"] + 1) not in args.onlychapters:
            continue
        outfile = gen_filename(args.outtmpl, chap, metadata, fmt)
        outfile = sanitize(outfile)
        start = msec_to_hour(int(chap["start"]))
        end = msec_to_hour(int(chap["end"]))
        command = [
            "ffmpeg",
            "-i",
            filename,
            "-ss",
            start,
            "-to",
            end,
        ]
        if args.codeccopy:
            command += ["-codec", "copy"]
        command += [outfile]

        vvprint("Command is {}".format(" ".join(command)))


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
