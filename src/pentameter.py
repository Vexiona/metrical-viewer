# Copyright (C) 2026 Ioan Andrei Nicolae
# SPDX-License-Identifier: GPL-3.0-only

"""Elegiac pentameter spreadsheet converter.

Pentameter scheme format: "DS_ ‖ DD_" or "DD_ ‖ DDÈ"
Each hemistich: 1-2 feet (D/S) + anceps (_ = long, È = short)
The ‖ marks the caesura.
"""

import sys
from common import (FOOT_TOKENS, FOOT_SIZE, find_columns, read_csv, process_rows,
                    compute_homodynia, ictus_positions, verify_homodynia,
                    detect_header_rows, tokenize_scheme)

# Pentameter feet plus the single closing element of each hemistich:
# _ = anceps realized long (l), È = realized short (e).
PENT_TOKENS = {**FOOT_TOKENS, '_': 'l', 'È': 'e'}
_PENT_BY_LENGTH = sorted(PENT_TOKENS, key=len, reverse=True)


def parse_pent_scheme(scheme_raw):
    """Convert pentameter scheme to internal format.

    Returns (scheme_string, caesura_position) or (None, None).
    """
    parts = scheme_raw.split('‖')
    if len(parts) != 2:
        return None, None

    # Tolerate stray markers (e.g. a leading footnote digit) rather than reject.
    first, second = (tokenize_scheme(p, PENT_TOKENS, _PENT_BY_LENGTH, strict=False)
                     for p in parts)

    caesura_pos = sum(FOOT_SIZE[code] for code in first)
    return ''.join(first + second), caesura_pos


def convert_verse(row, ref, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: [Pentameter] {ref}: no scheme", file=sys.stderr)
        return None

    our_scheme, caesura = parse_pent_scheme(scheme_raw)
    if our_scheme is None:
        print(f"Warning: [Pentameter] {ref}: unparseable scheme '{scheme_raw}'", file=sys.stderr)
        return None

    caesurae = [caesura] if caesura else []
    return our_scheme, caesurae


def load(csv_path, header_rows=None):
    """Load pentameter verses from spreadsheet. Returns verse dicts."""
    rows = read_csv(csv_path)
    if header_rows is None:
        header_rows = detect_header_rows(rows)
    cols = find_columns(rows, header_rows)
    print(f"Detected columns: {cols}", file=sys.stderr)
    verses, _ = process_rows(rows, header_rows, cols, convert_verse, meter='Pentameter')

    # Compute homodynia (ictus on 1st syllable)
    for v in verses:
        if v['syllables'] is not None and v['scheme']:
            v['homodynia'] = compute_homodynia(v['scheme'], v['syllables'], ictus='first')
            v['_ictus_positions'] = ictus_positions(v['scheme'], ictus='first')
        else:
            v['homodynia'] = []
            v['_ictus_positions'] = {}

    verify_homodynia(verses, rows, header_rows, cols, 'Pentameter')
    return verses
