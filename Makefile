all: build/viewer.html

build/viewer.html: data/hex.csv data/iamb.csv data/pentameter.csv src/build.py src/annotate.py src/common.py src/hexameter.py src/iamb.py src/pentameter.py src/header.html src/footer.html src/style.css src/viewer.js
	python3 src/build.py -o build/viewer.html

zip: build/viewer.html
	zip -9 build/anthologia-palatina.zip build/viewer.html data/*.csv data/*.xlsx src/*.py src/*.html src/*.css src/*.js Makefile LICENSE METHODOLOGY.md README.md

clean:
	rm -rf build/*

.PHONY: all clean zip
