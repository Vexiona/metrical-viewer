"""Elegiac pentameter spreadsheet converter.

Pentameter scheme format: "DS_ ‖ DD_" or "DD_ ‖ DDÈ"
Each hemistich: 1-2 feet (D/S) + anceps (_ = long, È = short)
The ‖ marks the caesura.
"""

import sys
from common import FOOT_SIZE, find_columns, read_csv, process_rows

HEADER_ROWS = 3


def parse_pent_scheme(scheme_raw):
    """Convert pentameter scheme to internal format.

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


def convert_verse(row, ref, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: {ref}: no scheme", file=sys.stderr)
        return None

    our_scheme, caesura = parse_pent_scheme(scheme_raw)
    if our_scheme is None:
        print(f"Warning: {ref}: unparseable scheme '{scheme_raw}'", file=sys.stderr)
        return None

    caesurae = [caesura] if caesura else []
    return our_scheme, caesurae


def load(csv_path):
    """Load pentameter verses from spreadsheet. Returns verse dicts."""
    rows = read_csv(csv_path)
    cols = find_columns(rows, HEADER_ROWS)
    print(f"Detected columns: {cols}", file=sys.stderr)
    verses, _ = process_rows(rows, HEADER_ROWS, cols, convert_verse, meter='Pentameter')
    return verses
