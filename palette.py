#!/usr/bin/env python3
"""Building a palette database of the provided directory of images."""

import sys

from pathlib import Path

import pickledb

from wand.image import Image

def main(): # pylint: disable=missing-function-docstring
    cache = pickledb.load(sys.argv[1], False)
    imagedir = sys.argv[2]

    for path in Path(imagedir).rglob('*'):
        if not path.is_file():
            continue

        count = 0
        count_red = 0
        count_green = 0
        count_blue = 0

        try:
            with Image(filename=path) as img:
                maxima = img.maxima
                if maxima < 65535:
                    print(f"NOPE (depth is {maxima}) on {path}")
                    continue

                blob = img.make_blob(format='RGB')
                for cursor in range(0, img.width * img.height * 3, 3):
                    count_red += blob[cursor]
                    count_green += blob[cursor + 1]
                    count_blue += blob[cursor + 2]
                    count += 1

            av_r = int(count_red/count)
            av_g = int(count_green/count)
            av_b = int(count_blue/count)

            print(f"{av_r:03.0f} {av_g:03.0f} {av_b:03.0f} ({maxima:03.0f}) : {path}")
            cache.set(str(path), [av_r, av_g, av_b])
        except IndexError:
            print(f"NOPE on {path}")

    cache.dump()
    print(f"{cache.totalkeys()} items in the cache")

if __name__ == "__main__":
    main()
