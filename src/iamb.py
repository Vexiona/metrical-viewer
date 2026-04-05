"""Iambic trimeter spreadsheet converter."""

import sys
from common import FOOT_SIZE, foot_starts, parse_scheme, find_columns, read_csv, process_rows, verify_bridges

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


def compute_bridges(scheme, syllables):
    """Compute Porson's bridge violation.

    Porson: 5th foot (index 4) is spondaic → word-end forbidden between its two longs.
    """
    violations = {}
    if len(scheme) < 6:
        return violations

    if scheme[4] == 'S':
        starts = foot_starts(scheme)
        idx = starts[4]  # first syllable of foot 5
        if idx < len(syllables) and syllables[idx][1]:
            violations['porson'] = idx

    return violations


def load(csv_path):
    """Load iambic verses from spreadsheet. Returns verse dicts."""
    rows = read_csv(csv_path)
    cols = find_columns(rows, HEADER_ROWS)
    print(f"Detected columns: {cols}", file=sys.stderr)
    verses, _ = process_rows(rows, HEADER_ROWS, cols, convert_verse, meter='Iamb')

    for v in verses:
        if v['syllables'] is not None and v['scheme']:
            v['bridges'] = compute_bridges(v['scheme'], v['syllables'])
        else:
            v['bridges'] = {}

    verify_bridges(verses, rows, HEADER_ROWS, cols, 'Iamb', ['porson'])
    return verses
