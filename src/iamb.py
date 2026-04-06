# Copyright (C) 2026 Ioan Andrei Nicolae
# SPDX-License-Identifier: GPL-3.0-only

"""Iambic trimeter spreadsheet converter."""

import sys
from common import (FOOT_SIZE, foot_starts, parse_scheme, find_columns, read_csv,
                    process_rows, verify_bridges, compute_homodynia, ictus_positions,
                    verify_homodynia)

HEADER_ROWS = 3

# Syllables per element for each foot type in iambic meter.
# Each foot has 2 elements (thesis + arsis).
# Trisyllabic feet have one resolved element spanning 2 syllables.
ELEMENT_SYLS = {
    'I': [1, 1], 'S': [1, 1], 'P': [1, 1],
    'A': [2, 1],  # anapest: resolved thesis (uu) + arsis (-)
    'b': [1, 2],  # tribrach: thesis (u) + resolved arsis (uu)
    'C': [1, 2],  # cretic: thesis (-) + resolved arsis (u-)
    'B': [2, 1],  # antibacchius: resolved thesis (--) + arsis (u)
}


def element_to_syllable(scheme, element):
    """Convert 1-based element (half-foot) position to 1-based syllable position."""
    syl_pos = 0
    el_count = 0
    for code in scheme:
        for el_syls in ELEMENT_SYLS.get(code, [1, 1]):
            el_count += 1
            syl_pos += el_syls
            if el_count == element:
                return syl_pos
    return element  # fallback


def convert_verse(row, ref, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: [Iamb] {ref}: no scheme", file=sys.stderr)
        return None

    our_scheme = parse_scheme(scheme_raw)
    if our_scheme is None:
        print(f"Warning: [Iamb] {ref}: unrecognized scheme '{scheme_raw}'", file=sys.stderr)
        return None

    caesurae = []
    col_idx = cols.get('caesura')
    if col_idx is not None:
        val = row[col_idx].strip() if len(row) > col_idx else ''
        if val.isdigit() and int(val) <= 12:
            caesurae = [element_to_syllable(our_scheme, int(val))]

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

    # Compute homodynia (ictus on last syllable of each foot)
    for v in verses:
        if v['syllables'] is not None and v['scheme']:
            v['homodynia'] = compute_homodynia(v['scheme'], v['syllables'], ictus='last')
            v['_ictus_positions'] = ictus_positions(v['scheme'], ictus='last')
        else:
            v['homodynia'] = []
            v['_ictus_positions'] = {}

    verify_bridges(verses, rows, HEADER_ROWS, cols, 'Iamb', ['porson'])
    verify_homodynia(verses, rows, HEADER_ROWS, cols, 'Iamb')
    return verses
