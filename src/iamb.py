"""Iambic trimeter spreadsheet converter."""

import sys
from common import parse_scheme, find_columns, read_csv, process_rows

HEADER_ROWS = 3


def convert_verse(row, ref, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: {ref}: no scheme", file=sys.stderr)
        return None

    our_scheme = parse_scheme(scheme_raw)
    if our_scheme is None:
        print(f"Warning: {ref}: unrecognized scheme '{scheme_raw}'", file=sys.stderr)
        return None

    caesurae = []
    col_idx = cols.get('caesura')
    if col_idx is not None:
        val = row[col_idx].strip() if len(row) > col_idx else ''
        if val.isdigit() and int(val) <= 12:
            caesurae = [int(val)]

    return our_scheme, caesurae


def load(csv_path):
    """Load iambic verses from spreadsheet. Returns verse dicts."""
    rows = read_csv(csv_path)
    cols = find_columns(rows, HEADER_ROWS)
    print(f"Detected columns: {cols}", file=sys.stderr)
    verses, _ = process_rows(rows, HEADER_ROWS, cols, convert_verse, meter='Iamb')
    return verses
