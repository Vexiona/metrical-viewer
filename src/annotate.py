#!/usr/bin/env python3
"""Generate metrical HTML annotation from verse text and scansion data.

Usage:
    python annotate.py verses.csv [-o output.html]

CSV columns: text,scheme,caesura
"""

import csv
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Foot types: code -> list of quantities per syllable
FEET = {
    'S': ['long', 'long'],              # Spondee
    'I': ['short', 'long'],             # Iamb
    'D': ['long', 'short', 'short'],    # Dactyl
    'T': ['long', 'short'],             # Trochee
    'A': ['short', 'short', 'long'],    # Anapest
    'P': ['short', 'short'],             # Pyrrhic
    'l': ['long'],                        # Lone long (anceps)
    'e': ['short'],                       # Lone short (anceps)
    'C': ['long', 'short', 'long'],       # Cretic
    'B': ['long', 'long', 'short'],       # Antibacchius
    'b': ['short', 'short', 'short'],     # Tribrach
}

# Standard feet per meter (anything else gets warning style)
STANDARD = {
    'Hexameter': set('DST'),
    'Iamb': set('SIP'),
    'Pentameter': set('DSle'),
}


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
            syllables.append((''.join(current), True))
            current = []
        else:
            current.append(ch)

    if current:
        syllables.append((''.join(current), False))

    return syllables


def expand_scheme(scheme):
    """Expand a scheme string into per-syllable (quantity, is_foot_end) list."""
    result = []
    for code in scheme:
        foot = FEET[code]
        for i, q in enumerate(foot):
            result.append((q, i == len(foot) - 1))
    return result


def generate_line(text, scheme, caesurae=None, standard_feet=None, ref='', line_class='line'):
    """Generate one <div class="line"> from annotated input.

    Args:
        text:     verse with # for syllable breaks, spaces for word breaks
        scheme:   string of foot codes (e.g. 'SISISI', 'DDDDDS')
        caesurae: list of 1-based syllable numbers after which caesurae fall
    """
    if caesurae is None:
        caesurae = []
    syllables = parse_syllables(text)
    quantities = expand_scheme(scheme)

    DASHES = set('―–')

    # Try merging elided syllables (ending with ') with the next syllable
    while len(syllables) > len(quantities):
        merged = False
        for i in range(len(syllables) - 1):
            if "'" in syllables[i][0]:
                merged_text = syllables[i][0] + '\u00a0' + syllables[i + 1][0]
                merged_wordend = syllables[i + 1][1]
                syllables = syllables[:i] + [(merged_text, merged_wordend)] + syllables[i + 2:]
                merged = True
                break
        if not merged:
            break

    # Merge dash-only syllables with neighbor
    while len(syllables) > len(quantities):
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
        if not merged:
            break

    if len(syllables) != len(quantities):
        raise ValueError(
            f"Syllable count mismatch: text has {len(syllables)}, "
            f"scheme '{scheme}' expands to {len(quantities)}"
        )

    spans = []
    for i, ((syl_text, is_wordend), (quantity, is_footend)) in enumerate(
        zip(syllables, quantities)
    ):
        classes = [quantity]
        if is_wordend:
            classes.append('wordend')
        if is_footend and i < len(syllables) - 1:
            classes.append('footend')
        if i + 1 in caesurae:
            classes.append('caesura')
        spans.append((classes, syl_text))

    lines = []
    for i, (classes, syl_text) in enumerate(spans):
        cls = ' '.join(classes)
        prefix = '' if i == 0 else '>'
        suffix = '>' if i == len(spans) - 1 else ''
        lines.append(f'{prefix}<span class="{cls}">{syl_text}</span{suffix}')

    inner = '\n'.join(lines)
    line_classes = line_class
    if standard_feet is not None and any(c not in standard_feet for c in scheme):
        line_classes += ' nonstandard'
    ref_span = f'<span class="ref">{ref}</span>' if ref else ''
    return f'    <div class="{line_classes}">{ref_span}\n{inner}\n    </div>'


def read_verses(csv_path, label=''):
    """Read a CSV file and return list of verse dicts."""
    tag = f"[{label}] " if label else ''
    std = STANDARD.get(label, None)
    verses = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for verse_num, row in enumerate(reader, start=1):
            epigram = row.get('epigram', '').strip()
            verse_id = row.get('verse', '').strip()
            text = row['text']
            scheme = row['scheme'].strip()
            caesura_str = row.get('caesura', '').strip()
            caesurae = [int(x) for x in caesura_str.split() if x] if caesura_str else []

            try:
                ep_num = float(epigram) if epigram else 0
            except ValueError:
                ep_num = 0
            try:
                v_num = float(verse_id) if verse_id else 0
            except ValueError:
                v_num = 0

            ref = verse_id or ''
            full_ref = f"{epigram}.{verse_id}" if epigram and verse_id else ''

            if not scheme:
                raw = text.replace('#', '').replace('  ', ' ')
                html = f'    <div class="line error"><span class="ref">{ref}</span>{raw}</div>'
                print(f"Warning: {tag}{full_ref}: no scheme", file=sys.stderr)
            else:
                try:
                    lc = 'line pent' if label == 'Pentameter' else 'line'
                    html = generate_line(text, scheme, caesurae, std, ref, lc)
                except ValueError as e:
                    raw = text.replace('#', '').replace('  ', ' ')
                    html = f'    <div class="line error"><span class="ref">{ref}</span>{raw}</div>'
                    print(f"Warning: {tag}{full_ref}: {e}", file=sys.stderr)

            verses.append({
                'epigram': ep_num,
                'verse': v_num,
                'label': label,
                'html': html,
            })
    return verses


def assemble_page(verses):
    """Build full page from sorted verse list."""
    header = (SCRIPT_DIR / 'header.html').read_text(encoding='utf-8')
    footer = (SCRIPT_DIR / 'footer.html').read_text(encoding='utf-8')

    parts = []
    current_ep = None
    for v in verses:
        if v['epigram'] != current_ep:
            if current_ep is not None:
                parts.append('    </div>')
            ep_display = int(v['epigram']) if v['epigram'] == int(v['epigram']) else v['epigram']
            parts.append('    <div class="epigram">')
            parts.append(f'    <div class="epigram-num"><span class="ref">ep. {ep_display}</span></div>')
            current_ep = v['epigram']
        parts.append(v['html'])
    if current_ep is not None:
        parts.append('    </div>')

    body = '\n'.join(parts)
    return header + '<div class="greektext">\n<div class="greektext-inner">\n' + body + '\n</div>\n</div>\n' + footer


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} label:input.csv [label:input.csv ...] [-o output.html]", file=sys.stderr)
        sys.exit(1)

    out_path = None
    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        out_path = sys.argv[idx + 1]
        args = sys.argv[1:idx] + sys.argv[idx + 2:]
    else:
        args = sys.argv[1:]

    all_verses = []
    for arg in args:
        if ':' in arg:
            label, csv_path = arg.split(':', 1)
        else:
            label = Path(arg).stem
            csv_path = arg
        all_verses.extend(read_verses(csv_path, label))

    # Sort by epigram, then verse number
    all_verses.sort(key=lambda v: (v['epigram'], v['verse']))

    if out_path:
        page = assemble_page(all_verses)
        Path(out_path).write_text(page, encoding='utf-8')
        print(f"Wrote {out_path}", file=sys.stderr)
    else:
        for v in all_verses:
            print(v['html'])


if __name__ == '__main__':
    main()
