# GDT610 artifacts

- result.json and target_summary.json: complete aggregate metrics.
- anchor_categories.tsv: fixed 42/4/34/7/11 inventory.
- calibration_grid.tsv and calibration_complete_mappings.tsv: all control
  coupling runs and maps.
- target_complete_mappings.tsv: all language, condition, view and unit maps.
- category_diagnostics.tsv: localized control and target failures.
- non_w_exact_matches.tsv: every non-injected exact reference match.
- synthetic_control_meta.json and synthetic_oracle_mapping.tsv: planted
  control construction.
- AGENT_VALIDATION.json: original 65-check scratch-bundle validation.
- VALIDATION.json: canonical GDT610 validation.

The multi-megabyte held decode tables are reproducible from the source but are
not committed; the compact tables preserve every decision-bearing result.
