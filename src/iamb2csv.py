#!/usr/bin/env python3
"""Convert iamb.csv spreadsheet to annotate.py-compatible CSV."""

import sys
from common import FOOT_MAP, find_columns, convert_feet, parse_args, read_csv, write_csv, process_rows

HEADER_ROWS = 2
NUM_FEET = 6


def convert_verse(row, verse_num, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: verse {verse_num}: no scheme", file=sys.stderr)
        return None

    our_scheme = convert_feet(row, cols, FOOT_MAP, NUM_FEET)
    if our_scheme is None:
        print(f"Warning: verse {verse_num}: unrecognized feet in scheme '{scheme_raw}'", file=sys.stderr)
        return None

    # Caesura: look for a 'caesura' column, otherwise try 'cezuri'
    caesura_str = ''
    for key in ['caesura', 'cezuri']:
        col_idx = cols.get(key)
        if col_idx is not None:
            val = row[col_idx].strip() if len(row) > col_idx else ''
            if val.isdigit() and int(val) <= 12:
                caesura_str = val
            break

    return our_scheme, caesura_str


def main():
    in_path, out_path = parse_args("Convert iamb.csv to annotate CSV")
    rows = read_csv(in_path)
    cols = find_columns(rows, HEADER_ROWS)
    print(f"Detected columns: {cols}", file=sys.stderr)
    output_rows, _ = process_rows(rows, HEADER_ROWS, cols, convert_verse)
    write_csv(output_rows, out_path)


if __name__ == '__main__':
    main()
