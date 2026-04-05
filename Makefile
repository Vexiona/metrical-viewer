all: build/viewer.html

build/hex_verses.csv: data/hex.csv src/hex2csv.py src/common.py
	python3 src/hex2csv.py data/hex.csv -o build/hex_verses.csv

build/iamb_verses.csv: data/iamb.csv src/iamb2csv.py src/common.py
	python3 src/iamb2csv.py data/iamb.csv -o build/iamb_verses.csv

build/pent_verses.csv: data/pentameter.csv src/pent2csv.py src/common.py
	python3 src/pent2csv.py data/pentameter.csv -o build/pent_verses.csv

build/viewer_raw.html: build/hex_verses.csv build/iamb_verses.csv build/pent_verses.csv src/annotate.py src/header.html src/footer.html
	python3 src/annotate.py Hexameter:build/hex_verses.csv Iamb:build/iamb_verses.csv Pentameter:build/pent_verses.csv -o build/viewer_raw.html

build/viewer.html: build/viewer_raw.html src/merge.py src/style.css src/viewer.js
	python3 src/merge.py build/viewer_raw.html -o build/viewer.html

clean:
	rm -rf build/*

.PHONY: all clean
