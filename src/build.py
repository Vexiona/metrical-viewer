#!/usr/bin/env python3
"""Build the metrical viewer HTML from source spreadsheets.

Usage:
    python build.py [-o output.html]

Reads data/hex.csv, data/iamb.csv, data/pentameter.csv and produces
a single self-contained HTML file.
"""

import sys
from pathlib import Path

import hexameter
import iamb
import pentameter
from annotate import verse_to_html, assemble_page

DATA_DIR = Path(__file__).parent.parent / 'data'


def main():
    out_path = None
    if '-o' in sys.argv:
        out_path = sys.argv[sys.argv.index('-o') + 1]

    # Load all verses from spreadsheets
    all_verses = []
    all_verses.extend(hexameter.load(DATA_DIR / 'hex.csv'))
    all_verses.extend(iamb.load(DATA_DIR / 'iamb.csv'))
    all_verses.extend(pentameter.load(DATA_DIR / 'pentameter.csv'))

    # Sort by epigram, then verse number
    for v in all_verses:
        try:
            v['_ep_num'] = float(v['epigram']) if v['epigram'] else 0
        except ValueError:
            v['_ep_num'] = 0
        try:
            v['_v_num'] = float(v['verse']) if v['verse'] else 0
        except ValueError:
            v['_v_num'] = 0

    all_verses.sort(key=lambda v: (v['_ep_num'], v['_v_num']))

    # Generate HTML for each verse
    for v in all_verses:
        v['_html'] = verse_to_html(v)

    if out_path:
        page = assemble_page(all_verses)
        Path(out_path).write_text(page, encoding='utf-8')
        print(f"Wrote {out_path}", file=sys.stderr)
    else:
        for v in all_verses:
            print(v['_html'])


if __name__ == '__main__':
    main()
