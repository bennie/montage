all: output.png

clean:
	rm -rf resized
	mkdir resized
	rm -f output.png data/resized.txt

resize:
	rm -f data/resized.txt
	make data/resized.txt


data resized:
	mkdir -p $@

data/goal.jpg: data
	@echo
	@echo You should put the file in data/goal.jpg we should pixelify
	@echo

data/palette.db: data/resized.txt
	./palette.py $@ resized

data/resized.txt: data resized
	./resizer.py
	touch $@

images:
	@echo
	@echo You should put the reference images in images/
	@echo

output.png: data/goal.jpg data/palette.db
	./build.pl data/palette.db data/goal.jpg $@
