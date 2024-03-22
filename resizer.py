#!/usr/bin/env python3
""" Crawl a given directory of images, and cache smaller versions for analysis """

import hashlib
import os

from pathlib import Path

import yaml

from wand.image import Image

from lib.montage import is_image, makethumb


def main(): # pylint: disable=missing-function-docstring
    with open('config.yaml', encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert os.path.exists(config['imagedir']), \
        f"ERROR: Image directory {config['imagedir']} dosen't exist"
    assert os.path.isdir(config['imagedir']), \
        f"ERROR: {config['imagedir']} is not a directory"
    assert os.access(config['imagedir'], os.R_OK), \
        f"ERROR: You do not have permissions to read from {config['imagedir']}"

    if not os.path.exists(config['thumbdir']):
        print(f"WARN: Directory {config['thumbdir']} dosen't exist, creating.")
        os.mkdir(config['thumbdir'])
    assert os.path.isdir(config['thumbdir']), \
        f"ERROR: {config['thumbdir']} is not a directory"
    assert os.access(config['thumbdir'], os.R_OK), \
        f"ERROR: You do not have permissions to read from {config['thumbdir']}"

    assert os.path.exists(config['goal'])
    with Image(filename=config['goal']) as img:
        height_ratio = img.height / img.width
        print(f"Height ratio is {height_ratio}")
        pref_width = config['default_size']
        pref_height = int(config['default_size'] * height_ratio)

    print('/-----------------------------------------------------------------------------\\')
    print('|         Filename         | Start Size | End Size |          Status          |')
    print('|--------------------------|------------|----------|--------------------------|')

    for path in Path(config['imagedir']).rglob('*'):
        if not path.is_file():
            continue
        if not is_image(path.name):
            continue

        md5 = hashlib.md5(str(path).encode()).hexdigest()
        outfile = os.path.join(config['thumbdir'], f"{md5}.{config['thumbnail_type']}")

        makethumb(path, outfile, height_ratio, pref_width, pref_height)

    print('\\-----------------------------------------------------------------------------/\n')


if __name__ == "__main__":
    main()
