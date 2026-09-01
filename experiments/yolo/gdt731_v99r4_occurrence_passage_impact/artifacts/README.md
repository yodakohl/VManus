# GDT731 artifacts

- `V99R3_V99R4_1039_OCCURRENCE_DELTA.tsv`: every changed exact token with its
  old/new whole meaning, family, confidence, evidence and rival.
- `V99R3_V99R4_911_LINE_RENDER_COMPARISON.tsv`: complete aligned before/after
  cell arrays and semicolon renderings for every affected line.
- `V99R3_V99R4_351_COMPLETE_LINE_COMPARISON.tsv`: affected lines whose inherited
  V48 unknown count is zero.
- `V99R4_50_TARGET_DENSE_PASSAGES.tsv` and
  `GDT731_V99R4_50_TARGET_DENSE_READER.md`: deterministic subset with the most
  changed target cells, in machine- and human-readable form; this is not a
  semantic-importance ranking.
- `V99R4_BLOCKER_CENSUS.tsv`: explicit dictionary and affected-passage counts
  for grade frames, indexed placeholders, strict generic material, audible
  structure and unknown cells.
- `V99R4_RENDER_QUALITY_SUMMARY.tsv`: exact before/after target-cell metrics.
- `V99R4_GDT696_OVERLAY_PARITY.tsv`: three untouched local-relation artifacts.
- `RESULT.json`: machine-readable result.
- `VALIDATION.json`: independent reconstruction and artifact hashes.
