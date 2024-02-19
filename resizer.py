#!/usr/bin/env python3

import os

from uuid import uuid4
from pathlib import Path
from wand.image import Image

# Config

debug = 1

imagedir = 'images'
thumbdir = 'cache'
default_size = 200
height_ratio = 1.5    # What do you multiply width to get height
thumbnail_type = 'png'

# Main

pref_height = int(default_size*height_ratio)
pref_width = default_size


def main():
    assert os.path.exists(imagedir), f"ERROR: Image directory {imagedir} dosen't exist"
    assert os.path.isdir(imagedir), f"ERROR: {imagedir} is not a directory"
    assert os.access(imagedir, os.R_OK), f"ERROR: You do not have permissions to read from {imagedir}"

    if not os.path.exists(thumbdir):
        print(f"WARN: Directory {thumbdir} dosen't exist, creating.")
        mkdir(thumbdir)
    assert os.path.isdir(thumbdir), f"ERROR: {thumbdir} is not a directory"
    assert os.access(thumbdir, os.R_OK), f"ERROR: You do not have permissions to read from {thumbdir}"

    if debug:
        print('/-----------------------------------------------------------------------------\\')
        print('|         Filename         | Start Size | End Size |          Status          |')
        print('|--------------------------|------------|----------|--------------------------|')

    for path in Path(imagedir).rglob('*'):
        if not path.is_file():
            continue
        if not is_image(path.name):
            continue

        uuid = uuid4()
        outfile = os.path.join(thumbdir, f"{uuid}.{thumbnail_type}")

        makethumb(path.name, path, outfile)

    print('\\-----------------------------------------------------------------------------/\n')

# Subroutines


def makethumb(name, infile, outfile):
    with Image(filename=infile) as img:
        width = img.width
        height = img.height

        if debug:
            print("|%26.26s|%11.11s |" % (name[-26:], f"{width}x{height}"), end='')

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

        if debug:
            print("%9.9s |" % (f"{width}x{height}"), end='')

        img.save(filename=outfile)

        if debug:
            print("%26.26s|" % (outfile[-26:]))


def is_image(name):
    ext = ('.bmp', '.gif', '.jpg', '.jpeg', '.png', '.psd')
    if name.lower().endswith(tuple(ext)):
        return True
    return False


if __name__ == "__main__":
    main()
