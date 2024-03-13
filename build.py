#!/usr/bin/env python3
"""Building a montage image from the palette database and cached images."""

import random
import sys

from math import ceil

import numpy as np
import pickledb
import yaml

from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


with open('config.yaml', encoding="utf-8") as f:
    config = yaml.safe_load(f)


def main(cache_file, goal_image, output_image): # pylint: disable=missing-function-docstring
    cache = pickledb.load(cache_file, False)

    if cache.totalkeys() == 0:
        print(f"NO CACHE: {sys.argv[1]}")
        sys.exit(1)
    else:
        print(f"We have {cache.totalkeys()} potential pixel images")

    # Calculate some basic sizes
    img = {'ref': Image(filename=goal_image)}
    img['out_width'] = img['ref'].width * config['upscale']
    img['out_height'] = img['ref'].height * config['upscale']
    img['height_ratio'] = img['ref'].height / img['ref'].width
    img['pixel_width'] = config['default_size']
    img['pixel_height'] = int(config['default_size'] * img['height_ratio'])

    print(f"Our output should be {img['out_width']} x {img['out_height']}")
    print(f"Height ratio is {img['height_ratio']}")

    # "big pixels" are where smaller images will form pixels
    bigpixels = calculate_big_pixels(img)
    draw_pixelated(img, bigpixels, "pixelated.jpg")

    # Find candidates to fill the big pixels
    locations = calculate_locations(cache, bigpixels)

    # Write the montage
    print(f"Writing the output image ({output_image}) of {len(bigpixels)} tiles")

    with Image(width=img['out_width'], height=img['out_height']) as out:
        for file, points in locations.items():
            print(f"{file} : ", end="")
            new_pixel = Image(filename=file)
            new_pixel.resize(height=img['pixel_height'],width=img['pixel_width'])

            total_count = len(points)
            count = 0
            for point in points:
                count += 1
                out.composite(new_pixel, point[0], point[1])
                print(f"\r{file} : {count} / {total_count}", end="")
            print("")

        out.save(filename=output_image)

# Subroutines

def calculate_big_pixels(img):
    """ Given an size, and "big pixel" size, divide up locations for big pixels. """

    bigpixels = []
    start_x = 0
    while start_x < img['out_width']:
        fin_x = start_x + img['pixel_width']
        fin_x = min(fin_x, img['out_width'])

        start_y = 0
        while start_y < img['out_height']:
            fin_y = start_y + img['pixel_height']
            fin_y = min(fin_y, img['out_height'])

            color_data = color_check(img['ref'], start_x, start_y, fin_x, fin_y)
            bigpixels.append([start_x, start_y, fin_x, fin_y, color_data])

            start_y = fin_y
        start_x = fin_x
    return bigpixels


def calculate_locations(cache, bigpixels):
    """ Given a set of big-pixels and their colors, find the best image to fill those locations """
    print('Calculating "big pixel" locations')
    locations = {}
    for bp in bigpixels:
        [file, delta] = find_closest(cache, *bp[4])
        cache_color = cache.get(file)
        print(f"{bp[0]},{bp[1]} : {bp[4]} -> {delta:.2f} -> {cache_color} : {file}")
        if file not in locations:
            locations[file] = []
        locations[file].append([bp[0], bp[1]])
    return locations


def color_check(img, start_x, start_y, fin_x, fin_y):
    """ Given an image handle, and bounds, calculate the average color """

    start_x = int(start_x/config['upscale'])
    start_y = int(start_y/config['upscale'])
    fin_x = ceil(fin_x/config['upscale'])
    fin_y = ceil(fin_y/config['upscale'])

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


def draw_pixelated(img, bigpixels, out_file):
    """ Draw a flat-color "pixelated" version of the output for error checking. """
    print("Drawing pixelated file.")
    draw = Drawing()
    for bp in bigpixels:
        draw.fill_color = Color(f"rgb({bp[4][0]}, {bp[4][1]}, {bp[4][2]})")
        draw.polygon([(bp[0],bp[1]),(bp[0],bp[3]),(bp[2],bp[3]),(bp[2],bp[1])])

    print(f"Writing pixelated output for reference: {out_file}")
    with Image(width=img['out_width'], height=img['out_height']) as pix:
        draw.draw(pix)
        pix.save(filename=out_file)


def find_closest(cache, r, g, b):
    """ Find nearby RGB matches in the cache using Euclidian distance """
    dist = 350  # 8-bit color reduced
    best = []
    point1 = np.array([r, g, b])

    for file in cache.getall():
        point2 = np.array(cache.get(file))
        tdist = np.linalg.norm(point1 - point2)

        if (tdist + config['color_distance']) < dist:  # Collect files of increasing precision
            best = [ file ]
            dist = tdist
        elif dist == tdist:
            best.append(file)

    choice = random.choice(best)
    return [ choice, dist ]


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
