all: output.png

clean:
	rm -f resized/*

resize: images
	mkdir -p resized
	./resizer.pl

data:
	mkdir -p $@

data/goal.jpg: data
	@echo
	@echo You should put the file in data/goal.jpg we should pixelify
	@echo

data/palette.db: data
	make clean resize 
	./palette.pl $@ resized/*.jpg	

images:
	@echo
	@echo You should put the reference images in images/
	@echo

output.png: data/goal.jpg data/palette.db
	./build.pl data/palette.db data/goal.jpg $@

