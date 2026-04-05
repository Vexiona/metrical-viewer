#!/usr/bin/env python3
"""Merge an HTML file with style.css and viewer.js into a single self-contained file.

Usage:
    python merge.py input.html [-o output.html]

Defaults to merged.html if no output specified.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} input.html [-o output.html]", file=sys.stderr)
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = 'merged.html'
    if '-o' in sys.argv:
        out_path = sys.argv[sys.argv.index('-o') + 1]

    html = Path(in_path).read_text(encoding='utf-8')
    css = (SCRIPT_DIR / 'style.css').read_text(encoding='utf-8')
    js = (SCRIPT_DIR / 'viewer.js').read_text(encoding='utf-8')

    html = html.replace(
        '  <link rel="stylesheet" type="text/css" href="style.css">',
        '  <style>\n' + css + '  </style>'
    )
    html = html.replace(
        '<script src="viewer.js"></script>',
        '<script>\n' + js + '</script>'
    )

    Path(out_path).write_text(html, encoding='utf-8')
    print(f"Wrote {out_path}", file=sys.stderr)


if __name__ == '__main__':
    main()
