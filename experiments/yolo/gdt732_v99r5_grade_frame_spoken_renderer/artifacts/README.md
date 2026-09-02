# Artifacts

- `V99R5_COMPLETE_SPOKEN_RENDERER.tsv`: canonical 1,586-row V99R4 dictionary
  plus the seven spoken-renderer metadata fields; every inherited column is
  byte-stable.
- `V99R5_175_GRADE_FRAME_READING_AUDIT.tsv`: one row per targeted reading with
  old/new wording, confidence, positive/counterevidence, scope and policy.
- `V99R5_2431_LICENSED_POSITION_OVERLAY.tsv`: exact cache position projection,
  including the thirty active bindings.
- `V99R5_1784_ACTIVE_SURFACE_SCOPE_CONTROLS.tsv`: same-surface positions that
  must not inherit the thirteen active readings.
- `V99R5_4752_RESIDUAL_CACHE_GRADE_FRAME_CELLS.tsv`: target-only full-cache
  V48-baseline residuals, split into 1,784 target-active controls, 2,908 other
  active out-of-scope cells, 52 superseded exact V48 cells with their current
  V99 context values, and eight contextual alias/merge cells.
- `V99R5_1661_AFFECTED_LINE_COMPARISON.tsv`: aligned full-cell before/after
  records for every changed line.
- `V99R5_50_TARGET_DENSE_PASSAGES.tsv` and
  `GDT732_V99R5_50_TARGET_DENSE_READER.md`: deterministic target-density sample;
  each passage explicitly lists any residual grade cells outside GDT732.
- `V99R5_RENDERER_CLASS_SUMMARY.tsv`, `V99R5_BLOCKER_DELTA.tsv` and
  `V99R5_RENDER_QUALITY_SUMMARY.tsv`: class, readability and preservation
  metrics.
- `V99R5_INHERITED_ARTIFACT_PARITY.tsv`: eight upstream byte-parity controls.
- `RESULT.json` and `VALIDATION.json`: machine-readable result and independent
  validation with output hashes.

The exhaustive position, residual and line tables are retained because they
are the evidence that active scope did not leak, non-target cells stayed
unchanged and the 4,752 residual grade cells are real rather than a reporting
artifact.
