"""Shared utilities for spreadsheet-to-CSV converters."""

import csv
import sys

# Master foot map — all known foot tokens across all meters
FOOT_MAP = {
    'D': 'D',       # Dactyl
    'S': 'S',       # Spondee (code may be remapped per meter)
    'T': 'T',       # Trochee
    'I': 'I',       # Iamb
    'P': 'P',       # Pyrrhic
    'Ap': 'A',      # Anapest
    'Cr': 'C',      # Cretic
    'Abacc': 'B',   # Antibacchius
    'Tb': 'b',      # Tribrach
}


def find_columns(rows, header_rows=3):
    """Auto-detect column indices by scanning header rows and first data row.

    Returns dict with keys: text, scheme, feet_start, and any caesura columns found.
    """
    cols = {}

    for i in range(min(header_rows, len(rows))):
        for j, val in enumerate(rows[i]):
            v = val.strip().lower()
            if (v == 'schemă' or v.startswith('schemă')) and 'scheme' not in cols:
                cols['scheme'] = j
            elif v == 'cezuri' or v == 'caesura':
                cols['caesura'] = j
            # Functional caesurae (hexameter)
            elif v == 'triem' and 'func_triem' not in cols:
                cols['func_triem'] = j
            elif v == 'penth' and 'func_penth' not in cols:
                cols['func_penth'] = j
            elif v == 'hephth' and 'func_hephth' not in cols:
                cols['func_hephth'] = j
            elif v == 'bucolică' or v.startswith('bucolic'):
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

    # Epigram and verse number columns
    for i in range(min(header_rows, len(rows))):
        for j, val in enumerate(rows[i]):
            # Normalize: collapse whitespace/newlines
            v = ' '.join(val.strip().lower().split())
            if v in ('epigr.', 'epigramă', 'ep.') and 'epigram' not in cols:
                cols['epigram'] = j
            elif v in ('nr. vers', 'nr vers') and 'verse_num' not in cols:
                cols['verse_num'] = j
    # Fallback: check for 'vers' in col 6+ area
    if 'verse_num' not in cols:
        for i in range(min(header_rows, len(rows))):
            for j, val in enumerate(rows[i]):
                v = ' '.join(val.strip().lower().split())
                if v == 'vers' and j >= 5:
                    cols['verse_num'] = j
                    break

    # Individual feet columns: look for known foot tokens after the scheme column
    if 'scheme' in cols and len(rows) > header_rows:
        sc = cols['scheme']
        data_row = rows[header_rows]
        for j in range(sc + 1, min(sc + 10, len(data_row))):
            val = data_row[j].strip()
            if val in FOOT_MAP:
                cols['feet_start'] = j
                break

    return cols


def convert_feet(row, cols, foot_map, num_feet):
    """Read feet from individual columns.

    Args:
        row: CSV row
        cols: column dict from find_columns
        foot_map: dict mapping spreadsheet tokens to annotate.py codes
        num_feet: expected number of feet

    Returns annotate.py scheme string or None on failure.
    """
    if 'feet_start' not in cols:
        return None

    feet_start = cols['feet_start']
    feet = []
    for j in range(feet_start, feet_start + num_feet):
        tok = row[j].strip() if len(row) > j else ''
        if not tok:
            continue
        code = foot_map.get(tok)
        if code is None:
            return None
        feet.append(code)

    if len(feet) == num_feet:
        return ''.join(feet)

    # Fallback: if one foot short, try last char of scheme string
    if len(feet) == num_feet - 1 and 'scheme' in cols:
        scheme_raw = row[cols['scheme']].strip().replace('Τ', 'T').replace('τ', 'T').replace(' ', '')
        if scheme_raw:
            last = scheme_raw[-1]
            code = foot_map.get(last)
            if code:
                feet.append(code)

    if len(feet) != num_feet:
        return None

    return ''.join(feet)


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
        convert_fn: function(row, verse_num, cols) -> (scheme, caesura_str) or None

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

        verse_num = len(output_rows) + 1
        result = convert_fn(row, verse_num, cols)

        if result is None:
            output_rows.append([epigram, verse, text, '', ''])
            skipped += 1
        else:
            scheme, caesura_str = result
            output_rows.append([epigram, verse, text, scheme, caesura_str])

    print(f"Converted {len(output_rows)} rows, skipped {skipped}", file=sys.stderr)
    return output_rows, skipped
