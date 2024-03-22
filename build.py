#!/usr/bin/env python3
"""Building a montage image from the palette database and cached images."""

import sys

import pickledb
import yaml

from wand.image import Image

from lib.montage import calculate_big_pixels, draw_pixelated, calculate_locations


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
    bigpixels = calculate_big_pixels(img, config['upscale'])
    draw_pixelated(img, bigpixels, "pixelated.jpg")

    # Find candidates to fill the big pixels
    locations = calculate_locations(cache, bigpixels, config['color_distance'])

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


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
