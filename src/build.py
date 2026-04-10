#!/usr/bin/env python3
# Copyright (C) 2026 Ioan Andrei Nicolae
# SPDX-License-Identifier: GPL-3.0-only

"""Build the metrical viewer HTML from source spreadsheets.

Usage:
    python build.py [-o output.html]

Reads data/hex.csv, data/iamb.csv, data/pentameter.csv and produces
a single self-contained HTML file.
"""

import csv
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

    # Determine epigram type from meters present
    from collections import defaultdict
    ep_meters = defaultdict(set)
    ep_csv_types = defaultdict(set)
    for v in all_verses:
        ep = v['_ep_num']
        ep_meters[ep].add(v['meter'])
        csv_type = v.get('verse_type', '')
        if csv_type:
            ep_csv_types[ep].add(csv_type)

    ep_types = {}
    for ep, meters in ep_meters.items():
        if 'Iamb' in meters:
            ep_types[ep] = 'iamb'
        elif 'Pentameter' in meters or meters == {'Hexameter', 'Pentameter'}:
            ep_types[ep] = 'distich'
        else:
            ep_types[ep] = 'hexameter'

    # Verify against spreadsheet type column
    TYPE_ALIASES = {'distih': 'distich', 'hex': 'hexameter', 'hex?': 'hexameter', 'iamb': 'iamb'}
    for ep, computed in ep_types.items():
        csv_types = ep_csv_types.get(ep, set())
        for csv_type in csv_types:
            csv_norm = TYPE_ALIASES.get(csv_type.lower().strip(), csv_type.lower().strip())
            if csv_norm != computed:
                print(f"Warning: epigram {int(ep) if ep == int(ep) else ep}: "
                      f"computed type '{computed}' but spreadsheet says '{csv_type}'",
                      file=sys.stderr)

    # Load authors
    ep_authors = {}
    authors_path = DATA_DIR / 'authors.csv'
    if authors_path.exists():
        with open(authors_path, encoding='utf-8-sig') as f:
            for row in csv.reader(f):
                if len(row) >= 2 and row[0].strip().isdigit():
                    author = row[1].strip()
                    if author.startswith('<') and author.endswith('>'):
                        author = '<' + author[1:-1].strip() + '>'
                    ep_authors[int(row[0].strip())] = author

    for v in all_verses:
        v['_ep_type'] = ep_types.get(v['_ep_num'], '')
        v['_ep_author'] = ep_authors.get(int(v['_ep_num']), '') if v['_ep_num'] == int(v['_ep_num']) else ''

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
