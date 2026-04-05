#!/usr/bin/env python3
"""Convert hex.csv spreadsheet to annotate.py-compatible CSV."""

import sys
from common import FOOT_MAP, find_columns, convert_feet, parse_args, read_csv, write_csv, process_rows

FOOT_SIZE = {'D': 3, 'd': 2, 'T': 2, 'I': 2, 'C': 3, 'B': 3, 'b': 3}

# Hexameter: spondee replacing dactyl = 'd'
HEX_FOOT_MAP = dict(FOOT_MAP)
HEX_FOOT_MAP['S'] = 'd'

HEADER_ROWS = 3
NUM_FEET = 6


def pick_caesurae(row, our_scheme, cols):
    """Collect all functional caesurae.

    M (masculine) = after the 1st syllable of the foot (the thesis/long)
    F (feminine) = after the 2nd syllable of the foot (1st short of dactyl)
    """
    def syll_count(n_feet):
        return sum(FOOT_SIZE.get(our_scheme[i], 0) for i in range(n_feet))

    def parse_mf(col_key):
        col_idx = cols.get(col_key)
        if col_idx is None:
            return 0
        val = row[col_idx].strip() if len(row) > col_idx else ''
        if val.endswith('F'):
            return 2
        if val.endswith('M'):
            return 1
        return 0

    positions = set()

    offset = parse_mf('func_triem')
    if offset:
        positions.add(syll_count(1) + offset)

    offset = parse_mf('func_penth')
    if offset:
        positions.add(syll_count(2) + offset)

    offset = parse_mf('func_hephth')
    if offset:
        positions.add(syll_count(3) + offset)

    col_buc = cols.get('func_bucolic')
    if col_buc is not None:
        val = row[col_buc].strip() if len(row) > col_buc else ''
        if val:
            positions.add(syll_count(4))

    return sorted(positions)


def convert_verse(row, verse_num, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: verse {verse_num}: no scheme", file=sys.stderr)
        return None

    our_scheme = convert_feet(row, cols, HEX_FOOT_MAP, NUM_FEET)
    if our_scheme is None:
        print(f"Warning: verse {verse_num}: unrecognized feet in scheme '{scheme_raw}'", file=sys.stderr)
        return None

    caesurae = pick_caesurae(row, our_scheme, cols)
    caesura_str = ' '.join(str(c) for c in caesurae)

    return our_scheme, caesura_str


def main():
    in_path, out_path = parse_args("Convert hex.csv to annotate CSV")
    rows = read_csv(in_path)
    cols = find_columns(rows, HEADER_ROWS)
    print(f"Detected columns: {cols}", file=sys.stderr)
    output_rows, _ = process_rows(rows, HEADER_ROWS, cols, convert_verse)
    write_csv(output_rows, out_path)


if __name__ == '__main__':
    main()
