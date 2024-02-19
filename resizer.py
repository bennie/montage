#!/usr/bin/env python3
""" Crawl a given directory of images, and cache smaller versions for analysis """

import os

from uuid import uuid4
from pathlib import Path
from wand.image import Image

# Config

DEBUG = 1

IMAGEDIR = 'images'
THUMBDIR = 'cache'
DEFAULT_SIZE = 200
HEIGHT_RATIO = 1.5    # What do you multiply width to get height
THUMBNAIL_TYPE = 'png'

# Main

PREF_HEIGHT = int(DEFAULT_SIZE*HEIGHT_RATIO)
PREF_WIDTH = DEFAULT_SIZE


def main(): # pylint: disable=missing-function-docstring
    assert os.path.exists(IMAGEDIR), f"ERROR: Image directory {IMAGEDIR} dosen't exist"
    assert os.path.isdir(IMAGEDIR), f"ERROR: {IMAGEDIR} is not a directory"
    assert os.access(IMAGEDIR, os.R_OK), \
        f"ERROR: You do not have permissions to read from {IMAGEDIR}"

    if not os.path.exists(THUMBDIR):
        print(f"WARN: Directory {THUMBDIR} dosen't exist, creating.")
        os.mkdir(THUMBDIR)
    assert os.path.isdir(THUMBDIR), f"ERROR: {THUMBDIR} is not a directory"
    assert os.access(THUMBDIR, os.R_OK), \
        f"ERROR: You do not have permissions to read from {THUMBDIR}"

    if DEBUG:
        print('/-----------------------------------------------------------------------------\\')
        print('|         Filename         | Start Size | End Size |          Status          |')
        print('|--------------------------|------------|----------|--------------------------|')

    for path in Path(IMAGEDIR).rglob('*'):
        if not path.is_file():
            continue
        if not is_image(path.name):
            continue

        uuid = uuid4()
        outfile = os.path.join(THUMBDIR, f"{uuid}.{THUMBNAIL_TYPE}")

        makethumb(path.name, path, outfile)

    print('\\-----------------------------------------------------------------------------/\n')

# Subroutines


def makethumb(name, infile, outfile):
    """ Given a display name, infile and outfile designation: Create the smaller image """
    with Image(filename=infile) as img:
        width = img.width
        height = img.height

        if DEBUG:
            xy = f"{width}x{height}"
            print(f"|{name[-26:]:26}|{xy:^12}|", end='')

        current_ratio = height / width

        new_height = new_width = None
        if current_ratio > HEIGHT_RATIO:  # tall and narrow
            delta = PREF_WIDTH / width
            new_height = int(height * delta)
            new_width = PREF_WIDTH
        elif HEIGHT_RATIO > current_ratio:  # Fat and wide
            delta = PREF_HEIGHT / height
            new_height = PREF_HEIGHT
            new_width = int(width * delta)
        else:  # perfect size
            new_height = PREF_HEIGHT
            new_width = PREF_WIDTH

        img.resize(new_width, new_height)
        img.crop(height=PREF_HEIGHT, width=PREF_WIDTH, gravity='center')

        width = img.width
        height = img.height

        if DEBUG:
            xy = f"{width}x{height}"
            print(f"{xy:^10}|", end='')

        img.save(filename=outfile)

        if DEBUG:
            print(f"{outfile[-26:]:26}|")


def is_image(name):
    """ Given an image name, check the extension to see if we consider it an image. """
    ext = ('.bmp', '.gif', '.jpg', '.jpeg', '.png', '.psd')
    if name.lower().endswith(tuple(ext)):
        return True
    return False


if __name__ == "__main__":
    main()
