# Software Methodology

The viewer software reads metrical annotations from CSV spreadsheets, verifies them against the Greek text, and produces a single self-contained HTML file with interactive visual overlays.

## Data pipeline

The syllable hyphenation, metrical schemes, and all other annotations were produced manually by the authors in spreadsheet form and exported as three CSV files (hexameter, iambic trimeter, elegiac pentameter). These are processed by meter-specific modules that parse the hyphenated Greek text into syllables, expand the metrical scheme into per-syllable quantities, and extract caesura positions from the spreadsheet columns. The software then computes metrical features independently from the text — bridge violations, diaereses, metrical caesurae, homodynia — and compares them against the spreadsheet annotations, reporting all discrepancies as warnings. These warnings were used to manually correct the dataset across multiple iterations.

## Interactive viewer

The output is a single HTML file with seven overlay toggles (colors, scansion marks, feet, diaereses, caesurae, bridges, homodynia), each applicable to the selected verse or to all verses simultaneously. Functional and metrical caesurae can be displayed independently. Verses are selected by clicking and navigated with arrow keys.

## Development process

The software was developed with significant use of generative AI. However, all behavior and output were independently verified by the authors. Should any reader find the software useful, we would appreciate if modifications to the code were contributed back to the project at https://github.com/Vexiona/metrical-viewer, or at least made publicly available. However, we do not impose any requirement to do so beyond what is needed under the GPLv3. 
