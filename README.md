# Anthologia Palatina - Metrical Viewer

Interactive viewer for the metrical analysis of Book I (Christian Epigrams) of the Anthologia Palatina (Codex Palatinus Graecus 23).

## Building

Requires Python 3. No external dependencies.

```
make            # build the viewer
make zip        # build and package everything into a zip
make clean      # remove build artifacts
```

The output is a single self-contained HTML file at `build/viewer.html`.

Build warnings (syllable mismatches, caesura verification, etc.) are printed to stderr. To capture them:

```
make 2> warnings.txt
```

## Project structure

```
data/               Spreadsheet data (CSV exports and source xlsx)
src/
  build.py          Entry point: assembles the viewer from all sources
  common.py         Shared parsing utilities (syllables, columns, schemes)
  hexameter.py      Hexameter-specific processing and verification
  iamb.py           Iambic trimeter processing
  pentameter.py     Elegiac pentameter processing
  annotate.py       HTML generation from parsed verse data
  header.html       Page header, toggle buttons, and legend
  footer.html       Page footer with license notice
  style.css         All styling
  viewer.js         Interactive viewer logic (toggles, selection, navigation)
```

## Using the viewer

Click a verse to select it. Use arrow keys to navigate between verses.

The toolbar toggles control overlays on the selected verse:

- **Colors** - syllable quantity highlighting (green = long, purple = short)
- **Scansion** - macron/breve marks below syllables
- **Feet** - dashed blue lines at foot boundaries
- **Diaereses** - solid blue lines where word-ends coincide with foot boundaries
- **Caesurae** - functional caesurae (red). The **M** button adds metrical caesurae (grey)
- **Bridges** - orange arcs marking bridge violations (Meyer, Hilberg, Hermann, Naeke, Porson)
- **Homodynia** - red dots where natural word accent falls on the metrical ictus

Each toggle has a **\*** button to apply the overlay to all verses at once.

## License

- **Text and data** (`data/`): Copyright 2026 Simona Nicolae, Cristian Simon. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
- **Code** (`src/`, `Makefile`): Copyright 2026 Ioan Andrei Nicolae. Licensed under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).
