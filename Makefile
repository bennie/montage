all: output.png

clean:
	rm -rf cache
	mkdir cache
	rm -f output.png data/resized.txt data/palette.db
	if [ ! -d data ]; then mkdir data; fi

resize:
	rm -f data/resized.txt
	make data/resized.txt

data/goal.jpg:
	@echo
	@echo You should put the file in data/goal.jpg we should pixelify
	@echo

data/palette.db: data/resized.txt
	./palette.py $@ cache

data/resized.txt:
	./resizer.py
	touch $@

output.png: data/goal.jpg data/palette.db
	./build.py data/palette.db data/goal.jpg $@
