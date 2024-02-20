#!/usr/bin/env python3
"""Building a montage image from the palette database and cached images."""

import random
import sys

from math import sqrt

import pickledb

from wand.color import Color
from wand.drawing import Drawing
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

    draw = Drawing()

    start_x = 0
    while start_x < width:
        fin_x = start_x + pixel_width
        fin_x = min(fin_x, width)

        start_y = 0
        while start_y < height:
            fin_y = start_y + pixel_height
            fin_y = min(fin_y, height)

            color_data = color_check(img, start_x, start_y, fin_x, fin_y, upscale)
            [file, delta] = find_closest(cache, color_data[0], color_data[1], color_data[2])

            draw.fill_color = Color(f"rgb({color_data[0]}, {color_data[1]}, {color_data[2]})")
            draw.polygon([(start_x,start_y),(start_x,fin_y),(fin_x,fin_y),(fin_x,start_y)])

            cache_color = cache.get(file)

            print(f"{count}: {start_x},{start_y} {fin_x},{fin_y} : {color_data} -> {delta} -> {cache_color} : {file}")

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

    with Image(width=width, height=height) as pix:
        draw.draw(pix)
        pix.save(filename='pixelated.jpg')

    print(f"Writing the output image ({output_image}) of {count} tiles")

    with Image(width=width, height=height) as out:
        for file in locations:
            print(f"{file} : ", end="")
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
                    print(f"\r{file} : {count} / {total_count}", end="")
                    out.composite(img, x, y)

            print("")
        out.save(filename=output_image)

# Subroutines

def color_check(img, start_x, start_y, fin_x, fin_y, upscale):
    """ Given an image handle, upscale, and location, calculate the average color """
    start_x = int(start_x/upscale)
    start_y = int(start_y/upscale)
    fin_x = int(fin_x/upscale) + 1 if fin_x % upscale else int(fin_x/upscale)
    fin_y = int(fin_y/upscale) + 1 if fin_y % upscale else int(fin_y/upscale)

    count = 0
    count_red = 0
    count_green = 0
    count_blue = 0

    with img[start_x:fin_x, start_y:fin_y] as cropped:
        blob = cropped.make_blob(format='RGB')
        for cursor in range(0, cropped.width * cropped.height * 3, 3):
            count_red += blob[cursor]
            count_green += blob[cursor + 1]
            count_blue += blob[cursor + 2]
            count += 1

    av_r = int(count_red/count)
    av_g = int(count_green/count)
    av_b = int(count_blue/count)

    return [av_r, av_g, av_b]



def find_closest(cache, r, g, b):
    """ Dig through the cache to find the nearest RGB match """
    dist = 350  # 8-bit color reduced
    best = []

    for file in cache.getall():
        tr, tg, tb = cache.get(file)
        tdist = int(sqrt((r-tr)**2 + (g-tg)**2 + (b-tb)**2))

        if tdist < dist:  # Collect files of increasing precision
            best = [ file ]
            dist = tdist
        elif dist == tdist:
            best.append(file)

        #  warn "Dist: $dist\n" if $dist <= 0;

    choice = random.choice(best)
    return [ choice, dist ]


if __name__ == "__main__":
    main()
