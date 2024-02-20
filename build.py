#!/usr/bin/env python3
"""Building a montage image from the palette database and cached images."""

import random
import sys

from math import ceil, sqrt

import pickledb

from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

DEFAULT_SIZE = 200
UPSCALE = 10
COLOR_DISTANCE = 50


def main(cache_file, goal_image, output_image): # pylint: disable=missing-function-docstring
    cache = pickledb.load(cache_file, False)

    if cache.totalkeys() == 0:
        print(f"NO CACHE: {sys.argv[1]}")
        sys.exit(1)

    print(f"We have {cache.totalkeys()} potential pixel images")

    img = Image(filename=goal_image)
    width = img.width * UPSCALE
    height = img.height * UPSCALE
    print(f"Our output should be {width} x {height}")

    # Calculate the "pixel" size
    height_ratio = img.height / img.width
    print(f"Height ratio is {height_ratio}")
    pixel_width = DEFAULT_SIZE
    pixel_height = int(DEFAULT_SIZE * height_ratio)

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

            color_data = color_check(img, start_x, start_y, fin_x, fin_y)
            [file, delta] = find_closest(cache, color_data[0], color_data[1], color_data[2])

            draw.fill_color = Color(f"rgb({color_data[0]}, {color_data[1]}, {color_data[2]})")
            draw.polygon([(start_x,start_y),(start_x,fin_y),(fin_x,fin_y),(fin_x,start_y)])

            cache_color = cache.get(file)

            print(f"{count}: {start_x},{start_y} {fin_x},{fin_y} : "
                  + f"{color_data} -> {delta} -> {cache_color} : {file}")

            if file not in locations:
                locations[file] = []
            locations[file].append([start_x, start_y])

            count += 1
            start_y = fin_y
        start_x = fin_x

    with Image(width=width, height=height) as pix:
        draw.draw(pix)
        pix.save(filename='pixelated.jpg')

    print(f"Writing the output image ({output_image}) of {count} tiles")

    with Image(width=width, height=height) as out:
        for file, points in locations.items():
            print(f"{file} : ", end="")
            img = Image(filename=file)
            img.resize(height=pixel_height,width=pixel_width)

            total_count = len(points)
            count = 0
            for point in points:
                out.composite(img, point[0], point[1])
                print(f"\r{file} : {count} / {total_count}", end="")
            print("")

        out.save(filename=output_image)

# Subroutines

def color_check(img, start_x, start_y, fin_x, fin_y):
    """ Given an image handle, UPSCALE, and location, calculate the average color """
    start_x = int(start_x/UPSCALE)
    start_y = int(start_y/UPSCALE)
    fin_x = ceil(fin_x/UPSCALE)
    fin_y = ceil(fin_y/UPSCALE)

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

        if (tdist + COLOR_DISTANCE) < dist:  # Collect files of increasing precision
            best = [ file ]
            dist = tdist
        elif dist == tdist:
            best.append(file)

        #  warn "Dist: $dist\n" if $dist <= 0;

    choice = random.choice(best)
    return [ choice, dist ]


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
