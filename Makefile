all: output.png

clean:
	rm -f resized/*

resize: 
	rm -f data/resized.txt
	make data/resized.txt
	

data:
	mkdir -p $@

data/goal.jpg: data
	@echo
	@echo You should put the file in data/goal.jpg we should pixelify
	@echo

data/palette.db: data/resized.txt
	./palette.pl $@ resized/*

data/resized.txt: data
	make clean
	mkdir -p resized
	./resizer.pl
	touch $@

images:
	@echo
	@echo You should put the reference images in images/
	@echo

output.png: data/goal.jpg data/palette.db
	./build.pl data/palette.db data/goal.jpg $@

