"""Shared utilities for spreadsheet-to-CSV converters."""

import csv
import sys

# All known foot tokens across all meters.
# Maps spreadsheet token -> annotate.py code.
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

# Syllable count per annotate.py foot code
FOOT_SIZE = {
    'D': 3, 'S': 2, 'T': 2, 'I': 2,
    'A': 3, 'C': 3, 'B': 3, 'b': 3, 'P': 2,
}


def parse_scheme(scheme_raw, num_feet=None):
    """Parse a scheme string into annotate.py format.

    Args:
        scheme_raw: scheme string from spreadsheet (e.g. 'DSDDDT', 'SApIApII')
        num_feet: if set, reject schemes that don't have exactly this many feet

    Returns annotate.py scheme string or None on failure.
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
    """Auto-detect column indices by scanning header rows and first data row.

    Returns dict with keys: text, scheme, epigram, verse_num, and any caesura columns found.
    """
    cols = {}

    for i in range(min(header_rows, len(rows))):
        for j, val in enumerate(rows[i]):
            v = ' '.join(val.strip().lower().split())
            if v == 'metrical pattern' and 'scheme' not in cols:
                cols['scheme'] = j
            elif v == 'caesura':
                cols['caesura'] = j
            elif v == 'epigramme no.' and 'epigram' not in cols:
                cols['epigram'] = j
            elif v == 'verse no.' and 'verse_num' not in cols:
                cols['verse_num'] = j
            # Functional caesurae (hexameter)
            elif v == 'triem' and 'func_triem' not in cols:
                cols['func_triem'] = j
            elif v == 'penth' and 'func_penth' not in cols:
                cols['func_penth'] = j
            elif v == 'hephth' and 'func_hephth' not in cols:
                cols['func_hephth'] = j
            elif v.startswith('bucolic'):
                cols['func_bucolic'] = j

    # Syllabified text: find the column with # markers in first data row
    if len(rows) > header_rows:
        data_row = rows[header_rows]
        for j in range(min(5, len(data_row))):
            if '#' in data_row[j]:
                cols['text'] = j
                break
    if 'text' not in cols:
        cols['text'] = 1

    return cols


def parse_args(description):
    """Parse common CLI args: input.csv [-o output.csv]"""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} input.csv [-o output.csv]", file=sys.stderr)
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = None
    if '-o' in sys.argv:
        out_path = sys.argv[sys.argv.index('-o') + 1]

    return in_path, out_path


def read_csv(path):
    """Read a CSV file with BOM handling."""
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.reader(f))


def write_csv(output_rows, out_path):
    """Write output CSV with header."""
    header = ['epigram', 'verse', 'text', 'scheme', 'caesura']
    if out_path:
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(output_rows)
        print(f"Wrote {out_path}", file=sys.stderr)
    else:
        writer = csv.writer(sys.stdout)
        writer.writerow(header)
        writer.writerows(output_rows)


def process_rows(rows, header_rows, cols, convert_fn):
    """Main processing loop shared by all converters.

    Args:
        rows: all CSV rows
        header_rows: number of header rows to skip
        cols: column dict from find_columns
        convert_fn: function(row, ref, cols) -> (scheme, caesura_str) or None

    Returns (output_rows, skipped_count).
    """
    text_col = cols['text']
    epigram_col = cols.get('epigram')
    verse_col = cols.get('verse_num')
    output_rows = []
    skipped = 0

    for i in range(header_rows, len(rows)):
        row = rows[i]
        text = row[text_col].strip() if len(row) > text_col else ''
        if not text:
            continue

        epigram = row[epigram_col].strip() if epigram_col and len(row) > epigram_col else ''
        verse = row[verse_col].strip() if verse_col and len(row) > verse_col else ''
        ref = f"{epigram}.{verse}" if epigram and verse else str(len(output_rows) + 1)

        result = convert_fn(row, ref, cols)

        if result is None:
            output_rows.append([epigram, verse, text, '', ''])
            skipped += 1
        else:
            scheme, caesura_str = result
            output_rows.append([epigram, verse, text, scheme, caesura_str])

    print(f"Converted {len(output_rows)} rows, skipped {skipped}", file=sys.stderr)
    return output_rows, skipped
