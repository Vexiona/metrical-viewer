#!/usr/bin/env python3
"""Convert pentameter.csv spreadsheet to annotate.py-compatible CSV.

Pentameter scheme format: "DS_ ‖ DD_" or "DD_ ‖ DDÈ"
Each hemistich: 1-2 feet (D/S) + anceps (_ = long, È = short)
The ‖ marks the caesura.
"""

import sys
from common import find_columns, parse_args, read_csv, write_csv, process_rows

FOOT_SIZE = {'D': 3, 'S': 2}

HEADER_ROWS = 3


def parse_pent_scheme(scheme_raw):
    """Convert pentameter scheme to annotate.py format.

    Returns (scheme_string, caesura_position) or (None, None).
    """
    clean = scheme_raw.replace(' ', '')
    parts = clean.split('‖')
    if len(parts) != 2:
        return None, None

    our_scheme = []
    caesura_pos = 0

    for hi, part in enumerate(parts):
        for c in part:
            if c in FOOT_SIZE:
                our_scheme.append(c)
                if hi == 0:
                    caesura_pos += FOOT_SIZE[c]
            elif c == '_':
                our_scheme.append('l')
                if hi == 0:
                    caesura_pos += 1
            elif c == 'È':
                our_scheme.append('e')
                if hi == 0:
                    caesura_pos += 1

    return ''.join(our_scheme), caesura_pos


def convert_verse(row, verse_num, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: verse {verse_num}: no scheme", file=sys.stderr)
        return None

    our_scheme, caesura = parse_pent_scheme(scheme_raw)
    if our_scheme is None:
        print(f"Warning: verse {verse_num}: unparseable scheme '{scheme_raw}'", file=sys.stderr)
        return None

    caesura_str = str(caesura) if caesura else ''
    return our_scheme, caesura_str


def main():
    in_path, out_path = parse_args("Convert pentameter.csv to annotate CSV")
    rows = read_csv(in_path)
    cols = find_columns(rows, HEADER_ROWS)
    print(f"Detected columns: {cols}", file=sys.stderr)
    output_rows, _ = process_rows(rows, HEADER_ROWS, cols, convert_verse)
    write_csv(output_rows, out_path)


if __name__ == '__main__':
    main()
