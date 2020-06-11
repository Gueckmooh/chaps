# CHAPter Split

This program aims to extract chapters from media files and, in the
future, will target chapter manipulation in media file (add, remove,
print, extract..).

## INSTALLATION

To install this script on Linux type:

    make install

## DESCRIPTION
**chaps** is a command-line program to split media files according to
ckapters. It uses FFmpeg and FFprobe to perform such extraction. Some
functions and features are strongly inspired by **youtube-dl**.

    chaps [OPTIONS] FILE

## OPTIONS
    -h, --help               Show this help message and exit
    -V, --version            Show program's version number and exit
    --restrict-filenames     Restrict filenames to only ASCII characters,
                             and avoid "&" and spaces in filenames
    -o TEMPLATE, --output TEMPLATE
                             Output filename template, see the "OUTPUT TEMPLATE"
                             for all the info.
                             [Default: "%(title)s-%(chapter-title)s.%(ext)s"]
    -c, --copy               Indicate to ffmpeg that the stream is not to be
                             re-encoded.
    -D, --dry-run            Do not write anything to disk.
    --only-chapters LIST     Indicate the chapters to extract, LIST is a comma
                             separated integer list e.g., 1,2,5. This indicates
                             to the program to extract only chapters 1, 2 and 5
    -p, --print-chapters     Prints chapter list.
    -C FILE, --chapter-file FILE
                             Use FILE to get chapters. See "CHAPTER FILE" for
                             more information.

### Verbosity Options
    -v, --verbose            Makes the program more talkative, duplicate for
                             more verbosity (e.g., -vvv).
    -q, --quiet              Makes the program quiet.
    -d, --debug              Print debug infos.
    -P, --progress           Print progress bar

## OUTPUT TEMPLATE

The `-o` option allows users to indicate a template for the output
file names. It is formated using **youtube-dl** flavour.

Allowed names along with sequence type are:

 - `chapter-title` (string): Chapter title
 - `chapter-id` (string): Chapter identifier
 - `chapter-index` (string): Chapter index
 - `title` (string): Video title
 - `ext` (string): Video filename extension

## CHAPTER FILE

The `-C` option allows user to write chapter timestamps in addition to
chapter title in a file and use it to split media according to those
chapters. This is usefull if your media file does not have any chapter
or if you want different chapter titles/timestamps.

Each line with a timestamp is parsed and the content of the line
without the timestamp becomes a chapter. This way you can take any
**youtube comment** with timestamps, paste it in a file and use it to
split media.
