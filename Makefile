all: output.png

clean:
	rm -rf resized
	mkdir resized
	rm -f output.png data/resized.txt data/palette.db
	mkdir data

resize:
	rm -f data/resized.txt
	make data/resized.txt

data/goal.jpg: data
	@echo
	@echo You should put the file in data/goal.jpg we should pixelify
	@echo

data/palette.db: data/resized.txt
	./palette.py $@ resized

data/resized.txt:
	./resizer.py
	touch $@

output.png: data/goal.jpg data/palette.db
	./build.pl data/palette.db data/goal.jpg $@
