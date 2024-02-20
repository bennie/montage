#!/usr/bin/env python3
""" Crawl a given directory of images, and cache smaller versions for analysis """

import os

import hashlib

from pathlib import Path
from wand.image import Image

# Config

DEBUG = 1

IMAGEDIR = 'images'
THUMBDIR = 'cache'
DEFAULT_SIZE = 200
THUMBNAIL_TYPE = 'png'

# Main


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

    assert os.path.exists('data/goal.jpg')
    with Image(filename='data/goal.jpg') as img:
        height_ratio = img.height / img.width
        print(f"Height ratio is {height_ratio}")
        pref_width = DEFAULT_SIZE
        pref_height = int(DEFAULT_SIZE * height_ratio)

    if DEBUG:
        print('/-----------------------------------------------------------------------------\\')
        print('|         Filename         | Start Size | End Size |          Status          |')
        print('|--------------------------|------------|----------|--------------------------|')

    for path in Path(IMAGEDIR).rglob('*'):
        if not path.is_file():
            continue
        if not is_image(path.name):
            continue

        md5 = hashlib.md5(str(path).encode()).hexdigest()
        outfile = os.path.join(THUMBDIR, f"{md5}.{THUMBNAIL_TYPE}")

        makethumb(path, outfile, height_ratio, pref_width, pref_height)

    print('\\-----------------------------------------------------------------------------/\n')

# Subroutines


def makethumb(path, outfile, height_ratio, pref_width, pref_height):
    """ Given a display name, infile and outfile designation: Create the smaller image """
    with Image(filename=path) as img:
        width = img.width
        height = img.height

        if DEBUG:
            xy = f"{width}x{height}"
            print(f"|{path.name[-26:]:26}|{xy:^12}|", end='')

        current_ratio = height / width

        new_height = new_width = None
        if current_ratio > height_ratio:  # tall and narrow
            delta = pref_width / width
            new_height = int(height * delta)
            new_width = pref_width
        elif height_ratio > current_ratio:  # Fat and wide
            delta = pref_height / height
            new_height = pref_height
            new_width = int(width * delta)
        else:  # perfect size
            new_height = pref_height
            new_width = pref_width

        img.resize(new_width, new_height)
        img.crop(height=pref_height, width=pref_width, gravity='center')

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
