# Copyright (C) 2026 Ioan Andrei Nicolae
# SPDX-License-Identifier: GPL-3.0-only

"""Hexameter spreadsheet converter."""

import sys
from common import (FOOT_SIZE, foot_starts, parse_scheme, find_columns, read_csv,
                    process_rows, verify_bridges, compute_homodynia, ictus_positions,
                    verify_homodynia)

NUM_FEET = 6
HEADER_ROWS = 3


def pick_caesurae(row, our_scheme, cols, prefix='func'):
    """Collect caesurae from columns with the given prefix.

    M (masculine) = after the 1st syllable of the foot (the thesis/long)
    F (feminine) = after the 2nd syllable of the foot (1st short of dactyl)
    """
    def syll_count(n_feet):
        return sum(FOOT_SIZE.get(our_scheme[i], 0) for i in range(n_feet))

    def parse_mf(col_key):
        """Return list of offsets (1=M, 2=F) from a cell that may have comma-separated values."""
        col_idx = cols.get(col_key)
        if col_idx is None:
            return []
        val = row[col_idx].strip() if len(row) > col_idx else ''
        if not val:
            return []
        offsets = []
        for part in val.split(','):
            part = part.strip()
            if part.endswith('F'):
                offsets.append(2)
            elif part.endswith('M'):
                offsets.append(1)
        return offsets

    positions = set()

    for offset in parse_mf(f'{prefix}_first'):
        positions.add(syll_count(0) + offset)

    for offset in parse_mf(f'{prefix}_triem'):
        positions.add(syll_count(1) + offset)

    for offset in parse_mf(f'{prefix}_penth'):
        positions.add(syll_count(2) + offset)

    for offset in parse_mf(f'{prefix}_hephth'):
        positions.add(syll_count(3) + offset)

    if prefix == 'func':
        col_buc = cols.get('func_bucolic')
        if col_buc is not None:
            val = row[col_buc].strip() if len(row) > col_buc else ''
            if val:
                positions.add(syll_count(4))

    return sorted(positions)


def convert_verse(row, ref, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: [Hexameter] {ref}: no scheme", file=sys.stderr)
        return None

    our_scheme = parse_scheme(scheme_raw, num_feet=NUM_FEET)
    if our_scheme is None:
        print(f"Warning: [Hexameter] {ref}: unrecognized scheme '{scheme_raw}'", file=sys.stderr)
        return None

    caesurae = pick_caesurae(row, our_scheme, cols, prefix='func')
    met_caesurae = pick_caesurae(row, our_scheme, cols, prefix='met')
    return our_scheme, caesurae, met_caesurae


def compute_bridges(scheme, syllables):
    """Compute bridge violations from scheme and pre-parsed syllables.

    Returns dict mapping bridge name to syllable index of the forbidden word-end.
    """
    violations = {}
    starts = foot_starts(scheme)

    # Meyer: 2nd foot (index 1) is dactylic, word-end between its two shorts
    if len(scheme) > 1 and scheme[1] == 'D':
        idx = starts[1] + 1  # 1st short of foot 2
        if idx < len(syllables) and syllables[idx][1]:
            violations['meyer'] = idx

    # Hermann: 4th foot (index 3) is dactylic, word-end between its two shorts
    if len(scheme) > 3 and scheme[3] == 'D':
        idx = starts[3] + 1
        if idx < len(syllables) and syllables[idx][1]:
            violations['hermann'] = idx

    # Hilberg: 2nd foot (index 1) is spondaic, word-end after foot 2
    if len(scheme) > 1 and scheme[1] == 'S':
        idx = starts[1] + FOOT_SIZE['S'] - 1
        if idx < len(syllables) and syllables[idx][1]:
            violations['hilberg'] = idx

    # Naeke: 4th foot (index 3) is spondaic, word-end after foot 4
    if len(scheme) > 3 and scheme[3] == 'S':
        idx = starts[3] + FOOT_SIZE['S'] - 1
        if idx < len(syllables) and syllables[idx][1]:
            violations['naeke'] = idx

    return violations


def verify_diaereses(verses, rows, header_rows, cols):
    """Compare spreadsheet diaeresis columns with computed diaereses.

    Uses pre-parsed syllables from verse dicts — same data that HTML generation uses.
    """
    has_diaer_cols = any(f'diaer_{f}' in cols for f in range(1, 6))
    if not has_diaer_cols:
        return

    data_rows = rows[header_rows:]
    text_col = cols['text']
    verse_idx = 0

    for i, row in enumerate(data_rows):
        text = row[text_col].strip() if len(row) > text_col else ''
        if not text:
            continue
        if verse_idx >= len(verses):
            break

        v = verses[verse_idx]
        verse_idx += 1

        if v['syllables'] is None or not v['scheme']:
            continue

        ref = f"{v['epigram']}.{v['verse']}"
        syllables = v['syllables']
        scheme = v['scheme']

        # Compute diaereses from pre-parsed syllables
        computed = set()
        syl_pos = 0
        for foot_num, code in enumerate(scheme, 1):
            syl_pos += FOOT_SIZE.get(code, 0)
            if syl_pos <= len(syllables) and syllables[syl_pos - 1][1] and foot_num < len(scheme):
                computed.add(foot_num)

        for foot in range(1, 6):
            col = cols.get(f'diaer_{foot}')
            if col is None:
                continue
            csv_val = row[col].strip() if len(row) > col else ''
            csv_has = bool(csv_val)
            comp_has = foot in computed
            if csv_has and not comp_has:
                print(f"Warning: [Hexameter] {ref}: diaeresis D{foot} in spreadsheet but not in text", file=sys.stderr)
            elif comp_has and not csv_has:
                print(f"Warning: [Hexameter] {ref}: diaeresis D{foot} in text but not in spreadsheet", file=sys.stderr)


def compute_met_caesura_positions(scheme, syllables):
    """Compute all metrical caesura positions from text.

    Checks feet 1-4 for word boundaries at M (after 1st syllable) and F
    (after 2nd syllable of trisyllabic feet) positions.
    Returns set of 1-based syllable positions.
    """
    positions = set()
    syl_pos = 0
    for foot in range(min(4, len(scheme))):
        code = scheme[foot]
        size = FOOT_SIZE.get(code, 0)
        # M: after 1st syllable
        m_pos = syl_pos + 1
        if m_pos - 1 < len(syllables) and syllables[m_pos - 1][1]:
            positions.add(m_pos)
        # F: after 2nd syllable (trisyllabic feet)
        if size >= 3:
            f_pos = syl_pos + 2
            if f_pos - 1 < len(syllables) and syllables[f_pos - 1][1]:
                positions.add(f_pos)
        syl_pos += size
    return positions


def position_to_column(pos, scheme):
    """Map a 1-based syllable position to spreadsheet column name and M/F value.

    Returns (column_name, value) like ('trihemim', '3M') or ('penthem', '5F'),
    or None if the position doesn't correspond to a standard caesura slot.
    The values use traditional half-foot numbering: 1, 3, 5, 7.
    """
    COL_NAMES = ['first foot', 'trihemim', 'penthem', 'hephth']
    HALF_FEET = [1, 3, 5, 7]
    syl_pos = 0
    for foot in range(min(4, len(scheme))):
        code = scheme[foot]
        size = FOOT_SIZE.get(code, 0)
        m_pos = syl_pos + 1
        f_pos = syl_pos + 2
        hf = HALF_FEET[foot]
        if pos == m_pos:
            return COL_NAMES[foot], f'{hf}M'
        if size >= 3 and pos == f_pos:
            return COL_NAMES[foot], f'{hf}F'
        syl_pos += size
    return None


def verify_met_caesurae(verses, cols):
    """Compare spreadsheet metrical caesurae with computed positions."""
    has_met_cols = any(k.startswith('met_') for k in cols)
    if not has_met_cols:
        return

    for v in verses:
        if v['syllables'] is None or not v['scheme']:
            continue
        ref = f"{v['epigram']}.{v['verse']}"
        csv_set = set(v.get('met_caesurae', []))
        computed = compute_met_caesura_positions(v['scheme'], v['syllables'])
        csv_only = csv_set - computed
        comp_only = computed - csv_set
        for pos in sorted(csv_only):
            info = position_to_column(pos, v['scheme'])
            col_hint = f" (column '{info[0]}')" if info else ''
            syllables = v['syllables']
            if pos - 1 < len(syllables) and not syllables[pos - 1][1]:
                print(f"Note: [Hexameter] {ref}: metrical caesura at position {pos} "
                      f"violated by elision{col_hint}", file=sys.stderr)
            else:
                print(f"Warning: [Hexameter] {ref}: metrical caesura at position {pos} "
                      f"in spreadsheet but not in text{col_hint}", file=sys.stderr)
        for pos in sorted(comp_only):
            info = position_to_column(pos, v['scheme'])
            if info:
                col_name, val = info
                hint = f" → write '{val}' in column '{col_name}'"
            else:
                hint = ''
            print(f"Warning: [Hexameter] {ref}: metrical caesura at position {pos} "
                  f"in text but not in spreadsheet{hint}", file=sys.stderr)


def verify_func_subset_met(verses):
    """Check that all functional caesurae (feet 1-4) are also marked as metrical."""
    for v in verses:
        if not v['scheme']:
            continue
        ref = f"{v['epigram']}.{v['verse']}"
        # Exclude bucolic diaeresis (end of foot 4) — metrical columns only cover caesurae within feet 1-4
        bucolic_pos = sum(FOOT_SIZE.get(v['scheme'][i], 0) for i in range(min(4, len(v['scheme']))))
        func_set = {p for p in v.get('caesurae', []) if p != bucolic_pos}
        met_set = set(v.get('met_caesurae', []))
        func_only = func_set - met_set
        for pos in sorted(func_only):
            info = position_to_column(pos, v['scheme'])
            if info:
                col_name, val = info
                hint = f" → write '{val}' in column '{col_name}'"
            else:
                hint = ''
            print(f"Warning: [Hexameter] {ref}: functional caesura at position {pos} "
                  f"not marked as metrical{hint}", file=sys.stderr)


def load(csv_path):
    """Load hexameter verses from spreadsheet. Returns verse dicts."""
    rows = read_csv(csv_path)
    cols = find_columns(rows, HEADER_ROWS)
    print(f"Detected columns: {cols}", file=sys.stderr)
    verses, _ = process_rows(rows, HEADER_ROWS, cols, convert_verse, meter='Hexameter')

    # Compute bridges for each verse
    for v in verses:
        if v['syllables'] is not None and v['scheme']:
            v['bridges'] = compute_bridges(v['scheme'], v['syllables'])
        else:
            v['bridges'] = {}

    # Compute homodynia (ictus on 1st syllable)
    for v in verses:
        if v['syllables'] is not None and v['scheme']:
            v['homodynia'] = compute_homodynia(v['scheme'], v['syllables'], ictus='first')
            v['_ictus_positions'] = ictus_positions(v['scheme'], ictus='first')
        else:
            v['homodynia'] = []
            v['_ictus_positions'] = {}

    verify_diaereses(verses, rows, HEADER_ROWS, cols)
    verify_bridges(verses, rows, HEADER_ROWS, cols, 'Hexameter',
                   ['meyer', 'hermann', 'naeke', 'hilberg'])
    verify_homodynia(verses, rows, HEADER_ROWS, cols, 'Hexameter')
    verify_met_caesurae(verses, cols)
    verify_func_subset_met(verses)
    return verses
