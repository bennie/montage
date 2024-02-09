# Montage

An image montage generator

## Summary

Remember those posters you might have seen? Where a character or scene from a movie was
made out of a montage of hundreds of images of said movie? Yeah. Those montages are neat.

This project is to be able to make my own from a give set of images.

## Directions

1. Copy an image you want to montage to "data/goal.jpg"

2. Edit "resizer.pl" and change the value of $default_image to your directory of source images.

3. Run "make"

4. Output will be "output.png"

If you wish to then repeat the process with a different image:

1. Change out "data/goal.jpg" with a new image

2. "make clean"

3. "make"

## License

[MIT](https://choosealicense.com/licenses/mit/)
