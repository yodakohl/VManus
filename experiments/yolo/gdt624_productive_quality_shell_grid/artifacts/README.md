# Artifacts

- `PAGE_ALLOWLIST.tsv`: the exact 179-page frequency scope.
- `GRID_CELLS.tsv`: all 48 predicted complete forms and three-reading counts.
- `GRID_OCCURRENCES.tsv`: 829 exact token occurrences with generated defaults.
- `QUADRANT_FRAME_COUNTS.tsv`: the 12 wrapper×ending count frames.
- `FACTOR_MARGINALS.tsv`: counts for each wrapper, axis, bit, and ending.
- `LOCAL_ONE_BIT_EDGES.tsv` and `LOCAL_EDGE_SUMMARY.tsv`: complete local
  one-change inventory.
- `WRAPPER_TRIPLETS.tsv`: 22 same-page bare/`o`/`qo` core triplets.
- `E_LENGTH_SERIES.tsv` and `E_LENGTH_LOCAL_SERIES.tsv`: 60 registered
  e-length cells and 83 local co-occurrences.
- `LOCAL_EXEMPLARS.tsv`: ten high-information contrast loci.
- `LOCAL_HERBAL_BINDINGS.tsv`: six adjacent quality-to-root/reproductive-part
  readings on previously opened images.
- `HISTORICAL_BINDING_COMPARATORS.tsv`: five manuscript mechanisms used to
  rank the `e` and `d` defaults.
- `PRODUCTIVE_READER.tsv`: one compositional German default for every cell.
- `CONCRETE_LINE_READINGS.tsv`: fifteen actual lines with unknowns preserved.
- `RESULT.json` and `VALIDATION.json`: canonical synthesis and replay
  certificate.

The occurrence table is retained because it is only 829 compact rows and is
needed to reproduce page/locus totals and exact local bindings. No manuscript
image bytes are committed.
