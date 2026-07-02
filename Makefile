SRC = src/build.py src/annotate.py src/common.py src/hexameter.py src/iamb.py src/pentameter.py src/header.html src/footer.html src/style.css src/viewer.js

all: build/viewer.html build/viewer3.html

build/viewer.html: data/hex.csv data/iamb.csv data/pentameter.csv data/book.json $(SRC)
	python3 src/build.py --data data -o build/viewer.html

build/viewer3.html: data3/hex.csv data3/pentameter.csv data3/book.json $(SRC)
	python3 src/build.py --data data3 -o build/viewer3.html

zip: build/viewer.html
	zip -9 build/anthologia-palatina.zip build/viewer.html data/*.csv data/*.xlsx data/*.pdf src/*.py src/*.html src/*.css src/*.js Makefile LICENSE METHODOLOGY.md README.md

clean:
	rm -rf build/*

.PHONY: all clean zip
