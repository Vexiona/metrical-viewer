# Copyright (C) 2026 Ioan Andrei Nicolae
# SPDX-License-Identifier: GPL-3.0-only

"""Shared utilities for spreadsheet parsing and verse annotation."""

import csv
import sys
import unicodedata

# All known foot tokens across all meters.
# Maps spreadsheet token -> internal code.
FOOT_TOKENS = {
    'D': 'D',       # Dactyl
    'S': 'S',       # Spondee
    'T': 'T',       # Trochee
    'I': 'I',       # Iamb
    'P': 'P',       # Pyrrhic
    'Ap': 'A',      # Anapest
    'Cr': 'C',      # Cretic
    'Abacc': 'B',   # Antibacchius
    'Tb': 'b',      # Tribrach
}

# Sorted longest-first for greedy matching
_TOKENS_BY_LENGTH = sorted(FOOT_TOKENS, key=len, reverse=True)

# Syllable count per foot code
FOOT_SIZE = {
    'D': 3, 'S': 2, 'T': 2, 'I': 2,
    'A': 3, 'C': 3, 'B': 3, 'b': 3, 'P': 2,
    'l': 1, 'e': 1,
}

# Foot types: code -> list of quantities per syllable
FEET = {
    'S': ['long', 'long'],
    'I': ['short', 'long'],
    'D': ['long', 'short', 'short'],
    'T': ['long', 'short'],
    'A': ['short', 'short', 'long'],
    'P': ['short', 'short'],
    'l': ['long'],
    'e': ['short'],
    'C': ['long', 'short', 'long'],
    'B': ['long', 'long', 'short'],
    'b': ['short', 'short', 'short'],
}

# Standard feet per meter (anything else gets 'nonstandard' class)
STANDARD = {
    'Hexameter': set('DST'),
    'Iamb': set('SIP'),
    'Pentameter': set('DSle'),
}

DASHES = {'\u2013', '\u2015'}  # EN DASH, HORIZONTAL BAR

GREEK_VOWELS = set('αεηιουωάέήίόύώὰὲὴὶὸὺὼᾶῆῖῦῶ'
                    'ἀἁἂἃἄἅἆἇἐἑἒἓἔἕἠἡἢἣἤἥἦἧ'
                    'ἰἱἲἳἴἵἶἷὀὁὂὃὄὅὐὑὒὓὔὕὖὗ'
                    'ὠὡὢὣὤὥὦὧᾀᾁᾂᾃᾄᾅᾆᾇᾐᾑᾒᾓᾔᾕᾖᾗ'
                    'ᾠᾡᾢᾣᾤᾥᾦᾧᾲᾳᾴᾷῂῃῄῇῒΐῢΰῲῳῴῷ'
                    'ΑΕΗΙΟΥΩ')


def parse_syllables(text):
    """Parse verse text into syllables with word-boundary info.

    Delimiters:
        space = syllable break + word boundary
        #     = syllable break within a word

    Returns list of (text, is_wordend) tuples.
    """
    syllables = []
    current = []

    for ch in text:
        if ch == '#':
            syllables.append((''.join(current), False))
            current = []
        elif ch == ' ':
            current.append('\u00a0')
            syllables.append((''.join(current), True))
            current = []
        else:
            current.append(ch)

    if current:
        syllables.append((''.join(current), False))

    return syllables


def merge_syllables(syllables):
    """Merge elided consonant-apostrophe syllables and dash-only syllables.

    Returns new syllables list.
    """
    # Merge consonant elisions (apostrophe after consonant) with next syllable
    i = 0
    while i < len(syllables) - 1:
        syl = syllables[i][0]
        apos = syl.find("'")
        if apos > 0 and syl[apos - 1].lower() not in GREEK_VOWELS:
            merged_text = syl + syllables[i + 1][0]
            merged_wordend = syllables[i + 1][1]
            syllables = syllables[:i] + [(merged_text, merged_wordend)] + syllables[i + 2:]
        i += 1

    # Merge dash-only syllables with neighbor
    merged = True
    while merged:
        merged = False
        for i in range(len(syllables)):
            if all(c in DASHES or c.isspace() for c in syllables[i][0]):
                if i < len(syllables) - 1:
                    merged_text = syllables[i][0] + syllables[i + 1][0]
                    merged_wordend = syllables[i + 1][1]
                    syllables = syllables[:i] + [(merged_text, merged_wordend)] + syllables[i + 2:]
                elif i > 0:
                    merged_text = syllables[i - 1][0] + syllables[i][0]
                    merged_wordend = syllables[i][1] or syllables[i - 1][1]
                    syllables = syllables[:i - 1] + [(merged_text, merged_wordend)]
                merged = True
                break

    return syllables


def foot_starts(scheme):
    """Return list of syllable indices where each foot starts."""
    starts = []
    pos = 0
    for code in scheme:
        starts.append(pos)
        pos += FOOT_SIZE.get(code, 0)
    return starts


def verify_bridges(verses, rows, header_rows, cols, meter, bridge_names):
    """Compare computed bridge violations with spreadsheet columns.

    bridge_names: list of bridge names to check (e.g. ['meyer', 'hermann']).
    Looks for cols['bridge_<name>'] for each.
    """
    bridge_cols = {name: cols.get(f'bridge_{name}') for name in bridge_names}
    if not any(v is not None for v in bridge_cols.values()):
        return

    data_rows = rows[header_rows:]
    text_col = cols['text']
    verse_idx = 0

    for row in data_rows:
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
        computed = v.get('bridges', {})

        for name, col_idx in bridge_cols.items():
            if col_idx is None:
                continue
            csv_val = row[col_idx].strip() if len(row) > col_idx else ''
            csv_has = bool(csv_val)
            comp_has = name in computed
            if csv_has and not comp_has:
                print(f"Warning: [{meter}] {ref}: bridge {name} in spreadsheet but not computed", file=sys.stderr)
            elif comp_has and not csv_has:
                print(f"Warning: [{meter}] {ref}: bridge {name} computed but not in spreadsheet", file=sys.stderr)


def has_accent(syllable):
    """Check if a Greek syllable contains an accented vowel."""
    nfd = unicodedata.normalize('NFD', syllable)
    return any(c in '\u0301\u0300\u0342' for c in nfd)


def compute_homodynia(scheme, syllables, ictus='first'):
    """Return sorted list of 1-based foot numbers with homodynia.

    ictus: 'first' (hex/pent) or 'last' (iamb)
    """
    result = []
    pos = 0
    for i, code in enumerate(scheme):
        size = FOOT_SIZE.get(code, 0)
        idx = pos if ictus == 'first' else pos + size - 1
        if idx < len(syllables) and has_accent(syllables[idx][0]):
            result.append(i + 1)
        pos += size
    return result


def ictus_positions(scheme, ictus='first'):
    """Return dict mapping 1-based foot number to syllable index of its ictus."""
    positions = {}
    pos = 0
    for i, code in enumerate(scheme):
        size = FOOT_SIZE.get(code, 0)
        idx = pos if ictus == 'first' else pos + size - 1
        positions[i + 1] = idx
        pos += size
    return positions


def verify_homodynia(verses, rows, header_rows, cols, meter):
    """Compare computed homodynia with spreadsheet column."""
    hom_col = cols.get('homodynia')
    if hom_col is None:
        return

    data_rows = rows[header_rows:]
    text_col = cols['text']
    verse_idx = 0

    for row in data_rows:
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
        computed = v.get('homodynia', [])

        csv_val = row[hom_col].strip() if len(row) > hom_col else ''
        csv_clean = csv_val.replace('_', '').strip()
        csv_feet = sorted(int(x) for x in csv_clean.split() if x.isdigit()) if csv_clean else []

        if computed != csv_feet:
            comp_only = set(computed) - set(csv_feet)
            csv_only = set(csv_feet) - set(computed)
            if csv_only:
                print(f"Warning: [{meter}] {ref}: homodynia feet {csv_only} in spreadsheet but not computed", file=sys.stderr)
            if comp_only:
                print(f"Warning: [{meter}] {ref}: homodynia feet {comp_only} computed but not in spreadsheet", file=sys.stderr)


def expand_scheme(scheme):
    """Expand a scheme string into per-syllable (quantity, is_foot_end) list."""
    result = []
    for code in scheme:
        foot = FEET[code]
        for i, q in enumerate(foot):
            result.append((q, i == len(foot) - 1))
    return result


def parse_scheme(scheme_raw, num_feet=None):
    """Parse a scheme string into internal format.

    Returns scheme string or None on failure.
    """
    result = []
    s = scheme_raw.strip()
    i = 0
    while i < len(s):
        if s[i] == ' ':
            i += 1
            continue
        matched = False
        for tok in _TOKENS_BY_LENGTH:
            if s[i:i+len(tok)] == tok:
                result.append(FOOT_TOKENS[tok])
                i += len(tok)
                matched = True
                break
        if not matched:
            return None
    if not result:
        return None
    if num_feet is not None and len(result) != num_feet:
        return None
    return ''.join(result)


def find_columns(rows, header_rows=3):
    """Auto-detect column indices by scanning header rows and first data row."""
    cols = {}

    for i in range(min(header_rows, len(rows))):
        for j, val in enumerate(rows[i]):
            v = ' '.join(val.strip().lower().split())
            if v.startswith('metrical pattern') and 'scheme' not in cols:
                cols['scheme'] = j
            elif v == 'caesura':
                cols['caesura'] = j
            elif v.startswith('epigram') and 'no' in v and 'epigram' not in cols:
                cols['epigram'] = j
            elif v == 'verse no.' and 'verse_num' not in cols:
                cols['verse_num'] = j
            elif v == 'first foot' and 'func_first' not in cols:
                cols['func_first'] = j
            elif v == 'first foot' and 'func_first' in cols and 'met_first' not in cols:
                cols['met_first'] = j
            elif v == 'trihem' and 'func_triem' not in cols:
                cols['func_triem'] = j
            elif v == 'trihem' and 'func_triem' in cols and 'met_triem' not in cols:
                cols['met_triem'] = j
            elif v == 'penthem' and 'func_penth' not in cols:
                cols['func_penth'] = j
            elif v == 'penthem' and 'func_penth' in cols and 'met_penth' not in cols:
                cols['met_penth'] = j
            elif v == 'hephthem' and 'func_hephth' not in cols:
                cols['func_hephth'] = j
            elif v == 'hephthem' and 'func_hephth' in cols and 'met_hephth' not in cols:
                cols['met_hephth'] = j
            elif v.startswith('bucolic'):
                cols['func_bucolic'] = j
            elif v in ('d1', 'd2', 'd3', 'd4', 'd4 (bucolic)', 'd5'):
                key = 'diaer_' + v[1]
                if key not in cols:
                    cols[key] = j
            elif v.startswith('porson') and 'bridge_porson' not in cols:
                cols['bridge_porson'] = j
            elif v.startswith('meyer') and 'bridge_meyer' not in cols:
                cols['bridge_meyer'] = j
            elif v.startswith('hermann') and 'bridge_hermann' not in cols:
                cols['bridge_hermann'] = j
            elif v.startswith('naeke') and 'bridge_naeke' not in cols:
                cols['bridge_naeke'] = j
            elif v.startswith('hilberg') and 'bridge_hilberg' not in cols:
                cols['bridge_hilberg'] = j
            elif v == 'manuscript version' and 'ms_text' not in cols:
                cols['ms_text'] = j
            elif v.startswith('homodynia') and 'homodynia' not in cols:
                cols['homodynia'] = j
            elif ('distich' in v or 'στίχον' in v) and 'verse_type' not in cols:
                cols['verse_type'] = j

    if len(rows) > header_rows:
        data_row = rows[header_rows]
        for j in range(min(5, len(data_row))):
            if '#' in data_row[j]:
                cols['text'] = j
                break
    if 'text' not in cols:
        cols['text'] = 1

    return cols


def read_csv(path):
    """Read a CSV file with BOM handling."""
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.reader(f))


def process_rows(rows, header_rows, cols, convert_fn, meter=''):
    """Main processing loop shared by all converters.

    Args:
        convert_fn: function(row, ref, cols) -> (scheme, caesurae_list) or None

    Returns (verse_dicts, skipped_count).
    Each verse dict has: epigram, verse, text, scheme, caesurae, meter,
    syllables, quantities (the last two are pre-parsed).
    """
    text_col = cols['text']
    epigram_col = cols.get('epigram')
    verse_col = cols.get('verse_num')
    type_col = cols.get('verse_type')
    ms_col = cols.get('ms_text')
    verses = []
    skipped = 0

    for i in range(header_rows, len(rows)):
        row = rows[i]
        text = row[text_col].strip() if len(row) > text_col else ''
        if not text:
            continue

        epigram = row[epigram_col].strip() if epigram_col and len(row) > epigram_col else ''
        verse = row[verse_col].strip() if verse_col and len(row) > verse_col else ''
        verse_type = row[type_col].strip() if type_col is not None and len(row) > type_col else ''
        ms_text = row[ms_col].strip() if ms_col is not None and len(row) > ms_col else ''
        ref = f"{epigram}.{verse}" if epigram and verse else str(len(verses) + 1)

        result = convert_fn(row, ref, cols)

        if result is None:
            verses.append({
                'epigram': epigram, 'verse': verse, 'text': text,
                'scheme': '', 'caesurae': [], 'meter': meter,
                'syllables': None, 'quantities': None,
                'verse_type': verse_type, 'ms_text': ms_text,
            })
            skipped += 1
        else:
            if len(result) == 3:
                scheme, caesurae, met_caesurae = result
            else:
                scheme, caesurae = result
                met_caesurae = []
            quantities = expand_scheme(scheme)
            syllables = parse_syllables(text)
            syllables = merge_syllables(syllables)
            if len(syllables) != len(quantities):
                print(f"Warning: [{meter}] {ref}: syllable count mismatch: "
                      f"text has {len(syllables)}, scheme '{scheme}' "
                      f"expands to {len(quantities)}", file=sys.stderr)
                syllables = None
                quantities = None
            verses.append({
                'epigram': epigram, 'verse': verse, 'text': text,
                'scheme': scheme, 'caesurae': caesurae, 'met_caesurae': met_caesurae,
                'meter': meter,
                'syllables': syllables, 'quantities': quantities,
                'verse_type': verse_type, 'ms_text': ms_text,
            })

    print(f"Converted {len(verses)} rows, skipped {skipped}", file=sys.stderr)
    return verses, skipped
