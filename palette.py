#!/usr/bin/env python3

import pickledb
import sys

from pathlib import Path
from wand.image import Image

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
            max = img.maxima
            blob = img.make_blob(format='RGB')
            for cursor in range(0, img.width * img.height * 3, 3):
                count_red += blob[cursor]
                count_green += blob[cursor + 1]
                count_blue += blob[cursor + 2]
                count += 1

        av_r = int(count_red/count)
        av_g = int(count_green/count)
        av_b = int(count_blue/count)

        print("%0.3d %0.3d %0.3d (%0.3d) : %s" % (av_r, av_g, av_b, max, path))
        cache.set(str(path), [av_r, av_g, av_b, max])
    except IndexError:
        print(f"NOPE on {path}")

cache.dump()
total = cache.totalkeys()
print(f"{total} items in the cache")
