""" Montage library: common utilities and functions """

import random

from math import ceil

import numpy as np

from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


def calculate_big_pixels(img, upscale):
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

            color_data = color_check(img['ref'], start_x, start_y, fin_x, fin_y, upscale)
            bigpixels.append([start_x, start_y, fin_x, fin_y, color_data])

            start_y = fin_y
        start_x = fin_x
    return bigpixels


def calculate_locations(cache, bigpixels, color_distance):
    """ Given a set of big-pixels and their colors, find the best image to fill those locations """
    print('Calculating "big pixel" locations')
    locations = {}
    for bp in bigpixels:
        [file, delta] = find_closest(cache, *bp[4], color_distance)
        cache_color = cache.get(file)
        print(f"{bp[0]},{bp[1]} : {bp[4]} -> {delta:.2f} -> {cache_color} : {file}")
        if file not in locations:
            locations[file] = []
        locations[file].append([bp[0], bp[1]])
    return locations


def color_check(img, start_x, start_y, fin_x, fin_y, upscale):  # pylint: disable=R0913,R0914
    """ Given an image handle, and bounds, calculate the average color """

    start_x = int(start_x/upscale)
    start_y = int(start_y/upscale)
    fin_x = ceil(fin_x/upscale)
    fin_y = ceil(fin_y/upscale)

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


def find_closest(cache, r, g, b, color_distance):
    """ Find nearby RGB matches in the cache using Euclidian distance """
    dist = 350  # 8-bit color reduced
    best = []
    point1 = np.array([r, g, b])

    for file in cache.getall():
        point2 = np.array(cache.get(file))
        tdist = np.linalg.norm(point1 - point2)

        if (tdist + color_distance) < dist:  # Collect files of increasing precision
            best = [ file ]
            dist = tdist
        elif dist == tdist:
            best.append(file)

    choice = random.choice(best)
    return [ choice, dist ]

def is_image(name):
    """ Given an image name, check the extension to see if we consider it an image. """
    ext = ('.bmp', '.gif', '.jpg', '.jpeg', '.png', '.psd')
    if name.lower().endswith(tuple(ext)):
        return True
    return False


def makethumb(path, outfile, height_ratio, pref_width, pref_height):
    """ Given a display name, infile and outfile designation: Create the smaller image """
    with Image(filename=path) as img:
        width = img.width
        height = img.height

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

        xy = f"{width}x{height}"
        print(f"{xy:^10}|", end='')

        img.save(filename=outfile)

        print(f"{outfile[-26:]:26}|")
