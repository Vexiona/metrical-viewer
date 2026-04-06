# Copyright (C) 2026 Ioan Andrei Nicolae
# SPDX-License-Identifier: GPL-3.0-only

"""HTML generation from pre-parsed verse data."""

from pathlib import Path
from common import STANDARD

SCRIPT_DIR = Path(__file__).parent


def generate_line(v):
    """Generate one <div class="line"> from a verse dict.

    Expects v to have: scheme, caesurae, meter, verse, syllables, quantities.
    syllables and quantities are pre-parsed by process_rows.
    """
    ref = v['verse'] or ''
    scheme = v['scheme']
    meter = v['meter']
    caesurae = v.get('caesurae', [])
    met_caesurae = v.get('met_caesurae', [])
    bridge_positions = set(v.get('bridges', {}).values())
    homodynia_feet = set(v.get('homodynia', []))
    ictus_pos = v.get('_ictus_positions', {})
    homodynia_syls = {ictus_pos[f] for f in homodynia_feet if f in ictus_pos}
    syllables = v['syllables']
    quantities = v['quantities']

    line_class = 'line pent' if meter == 'Pentameter' else 'line'
    std = STANDARD.get(meter)
    if std is not None and any(c not in std for c in scheme):
        line_class += ' nonstandard'

    spans = []
    for i, ((syl_text, is_wordend), (quantity, is_footend)) in enumerate(
        zip(syllables, quantities)
    ):
        classes = [quantity]
        if is_wordend:
            classes.append('wordend')
        if is_footend and i < len(syllables) - 1:
            classes.append('footend')
            if is_wordend:
                classes.append('diaeresis')
        if i + 1 in caesurae:
            classes.append('caesura')
        if i + 1 in met_caesurae:
            classes.append('met-caesura')
        if i in bridge_positions:
            classes.append('bridge')
        if i in homodynia_syls:
            classes.append('homodynia')
        spans.append((classes, syl_text))

    lines = []
    for i, (classes, syl_text) in enumerate(spans):
        cls = ' '.join(classes)
        prefix = '' if i == 0 else '>'
        suffix = '>' if i == len(spans) - 1 else ''
        lines.append(f'{prefix}<span class="{cls}">{syl_text}</span{suffix}')

    inner = '\n'.join(lines)
    ref_span = f'<span class="ref">{ref}</span>' if ref else ''
    return f'    <div class="{line_class}">{ref_span}\n{inner}\n    </div>'


def verse_to_html(v):
    """Convert a verse dict to HTML. Handles errors and missing data."""
    ref = v['verse'] or ''

    if not v['scheme'] or v['syllables'] is None:
        raw = v['text'].replace('#', '').replace('  ', ' ')
        return f'    <div class="line error"><span class="ref">{ref}</span>{raw}</div>'

    return generate_line(v)


def assemble_page(verses):
    """Build full self-contained page from sorted verse list."""
    header = (SCRIPT_DIR / 'header.html').read_text(encoding='utf-8')
    footer = (SCRIPT_DIR / 'footer.html').read_text(encoding='utf-8')

    parts = []
    current_ep = None
    for v in verses:
        if v['_ep_num'] != current_ep:
            if current_ep is not None:
                parts.append('    </div>')
            ep_display = int(v['_ep_num']) if v['_ep_num'] == int(v['_ep_num']) else v['_ep_num']
            parts.append('    <div class="epigram">')
            parts.append(f'    <div class="epigram-num"><span class="ref">ep. {ep_display}</span></div>')
            current_ep = v['_ep_num']
        parts.append(v['_html'])
    if current_ep is not None:
        parts.append('    </div>')

    body = '\n'.join(parts)
    page = header + '<div class="greektext">\n<div class="greektext-inner">\n' + body + '\n</div>\n</div>\n' + footer

    # Inline CSS and JS
    css = (SCRIPT_DIR / 'style.css').read_text(encoding='utf-8')
    js = (SCRIPT_DIR / 'viewer.js').read_text(encoding='utf-8')

    page = page.replace(
        '  <link rel="stylesheet" type="text/css" href="style.css">',
        '  <style>\n' + css + '  </style>'
    )
    page = page.replace(
        '<script src="viewer.js"></script>',
        '<script>\n' + js + '</script>'
    )

    return page
