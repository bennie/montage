# Montage

An image montage generator

## Summary

Remember those posters you might have seen? Where a character or scene from a movie was
made out of a montage of hundreds of images of said movie? Yeah. Those montages are neat.

![The Fluffiest Death](examples/death.jpg?raw=true "The Fluffiest Death")

![Closeup of Pixels](examples/closeup.jpg?raw=true "Closeup of 'Pixels'")

This project is to be able to make my own from a given set of images.

## Directions

1. Copy an image you want to montage to "data/goal.jpg"

2. Edit "resizer.py" and change the value of $default_image to your directory of source images.

3. Run "make"

4. Output will be "output.png"

If you wish to then repeat the process with a different image:

1. Change out "data/goal.jpg" with a new image

2. "make clean"

3. "make"

## License

GPL 2 - See "LICENSE" in repo.
