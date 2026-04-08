# Metrical Viewer

Interactive viewer for the metrical analysis of ancient Greek verse. Built for the dataset of Book I (Christian Epigrams) of the Anthologia Palatina.

## Setup

Clone with the data submodule:

```
git clone --recurse-submodules https://github.com/Vexiona/metrical-viewer.git
```

Or, if already cloned:

```
git submodule update --init
```

## Building

Requires Python 3. No external dependencies.

```
make            # build the viewer
make zip        # package everything into a zip
make clean      # remove build artifacts
```

The output is a single self-contained HTML file at `build/viewer.html`.

## Using the viewer

Click a verse to select it. Use arrow keys to navigate between verses.

The toolbar toggles control overlays on the selected verse:

- **Colors** - syllable quantity highlighting (green = long, purple = short)
- **Scansion** - macron/breve marks below syllables
- **Feet** - dashed blue lines at foot boundaries
- **Diaereses** - solid blue lines where word-ends coincide with foot boundaries
- **Caesurae** - functional caesurae (red). The **M** button adds metrical caesurae (grey)
- **Bridges** - orange arcs marking bridge violations
- **Homodynia** - red dots where natural word accent falls on the metrical ictus

Each toggle has a **\*** button to apply the overlay to all verses at once.

## License

Code is licensed under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html). Copyright 2026 Ioan Andrei Nicolae.

The data submodule is separately licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Copyright 2026 Simona Nicolae, Cristian Șimon.
