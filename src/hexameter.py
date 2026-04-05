"""Hexameter spreadsheet converter."""

import sys
from common import FOOT_SIZE, foot_starts, parse_scheme, find_columns, read_csv, process_rows, verify_bridges

NUM_FEET = 6
HEADER_ROWS = 3


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


def convert_verse(row, ref, cols):
    scheme_col = cols.get('scheme')
    scheme_raw = row[scheme_col].strip() if scheme_col and len(row) > scheme_col else ''

    if not scheme_raw:
        print(f"Warning: {ref}: no scheme", file=sys.stderr)
        return None

    our_scheme = parse_scheme(scheme_raw, num_feet=NUM_FEET)
    if our_scheme is None:
        print(f"Warning: {ref}: unrecognized scheme '{scheme_raw}'", file=sys.stderr)
        return None

    caesurae = pick_caesurae(row, our_scheme, cols)
    return our_scheme, caesurae


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

    verify_diaereses(verses, rows, HEADER_ROWS, cols)
    verify_bridges(verses, rows, HEADER_ROWS, cols, 'Hexameter',
                   ['meyer', 'hermann', 'naeke', 'hilberg'])
    return verses
