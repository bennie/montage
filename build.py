#!/usr/bin/env python3
"""Building a montage image from the palette database and cached images."""

import random
import sys

from math import sqrt

import pickledb

from wand.image import Image


def main(): # pylint: disable=missing-function-docstring
    cache = pickledb.load(sys.argv[1], False)
    goal_image = sys.argv[2]
    output_image = sys.argv[3]

    if cache.totalkeys() == 0:
        print(f"NO CACHE: {sys.argv[1]}")
        sys.exit(1)

    pixel_width = 100
    pixel_height = 77
    upscale = 10

    print(f"We have {cache.totalkeys()} potential pixel images")

    img = Image(filename=goal_image)
    width = img.width * upscale
    height = img.height * upscale
    print(f"Our output should be {width} x {height}")

    locations = {}
    count = 1

    start_x = 0
    while start_x < width:
        fin_x = start_x + pixel_width
        start_y = 0
        while start_y < height:
            fin_y = start_y + pixel_height

            color_data = color_check(img, start_x, start_y, fin_x, fin_y, upscale=1)
            [file, delta] = find_closest(cache, color_data[0], color_data[1], color_data[2])

            print(f"{count}: {start_x},{start_y} : {delta} : {file}")

            if file not in locations:
                locations[file] = {}
            if start_x not in locations[file]:
                locations[file][start_x] = {}
            if start_y not in locations[file][start_x]:
                locations[file][start_x][start_y] = 0

            locations[file][start_x][start_y] += 1

            count += 1
            start_y = fin_y
        start_x = fin_x

    print(f"Writing the output image ({output_image}) of {count} tiles")

    with Image(width=width, height=height) as out:
        for file in locations.items():
            print("{file} : ", end="")
            img = Image(filename=file)
            img.resize(height=pixel_height,width=pixel_width)

            total_count = 0
            for x in locations[file]:
                for y in locations[file][x]:
                    total_count += 1

            count = 0
            for x in locations[file]:
                for y in locations[file][x]:
                    count += 1
                    print(f"\r{file} : {count} / {total_count}")
                    out.composite(img, x, y)

            print("")
        out.save(filename=output_image)

# Subroutines

def color_check(img, start_x, start_y, fin_x, fin_y, upscale=1):
    """ Given an image handle, upscale, and location, calculate the average color """
    start_x = int(start_x/upscale)
    start_y = int(start_y/upscale)
    fin_x = int(fin_x/upscale) + 1 if fin_x % upscale else fin_x/upscale
    fin_y = int(fin_y/upscale) + 1 if fin_y % upscale else fin_y/upscale

    count = 0
    count_red = 0
    count_green = 0
    count_blue = 0

    blob = img.make_blob(format='RGB')
    for cursor in range(0, img.width * img.height * 3, 3):
        count_red += blob[cursor]
        count_green += blob[cursor + 1]
        count_blue += blob[cursor + 2]
        count += 1

    av_r = int(count_red/count)
    av_g = int(count_green/count)
    av_b = int(count_blue/count)

    return [av_r, av_g, av_b]



def find_closest(cache, r_in, g_in, b_in):
    """ Dig through the cache to find the nearest RGB match """
    dist = 350  # 8-bit color reduced
    best = []

    [r, g, b] = resample(r_in, g_in, b_in, dist)

    for file in cache.getall():
        info = cache.get(file)
        [tr, tg, tb] = resample(info[0], info[1], info[2], dist)
        tdist = int(sqrt((r-tr)**2 + (g-tg)**2 + (b-tb)**2))

        if tdist < dist:  # Collect files of increasing precision
            best = [ file ]
            dist = tdist
        elif dist == tdist:
            best.append(file)

        #  warn "Dist: $dist\n" if $dist <= 0;

    choice = random.choice(best)
    return [ choice, dist ]


def resample(r_in, g_in, b_in, depth):
    """ Calculate resampling drift (positive) for a give RGB value """
    resample_factor = ( depth + 1 ) / 256
    r = int(r_in/resample_factor)
    g = int(g_in/resample_factor)
    b = int(b_in/resample_factor)

    if r_in % resample_factor:
        r += 1
    if g_in % resample_factor:
        g += 1
    if b_in % resample_factor:
        b += 1

    return [r, g, b]


if __name__ == "__main__":
    main()
