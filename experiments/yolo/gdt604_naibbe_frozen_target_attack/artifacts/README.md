# Artifacts

- `gdt604_folio_split.json`: immutable 68/23 physical-folio split.
- `gdt604_target_rows.tsv`: complete guarded f84-free source rows.
- `gdt604_target_segmentation_u115.json`, `_u132.json`, `_u138.json`: complete
  train-only segmentation variants; U=138 is primary.
- `gdt604_target_key_freeze.json`: all 36 train-only language/null keys.
- `gdt604_target_result.json`: compact held evaluation and gate decisions.
- `gdt604_reference_calibration.json`: readable-reference instrument check.
- `gdt604_top_lines_*.tsv`: complete 20-line output panels per language.
- `GDT604_TOP_LINES_FULL.md`: readable untruncated appendix.
- `gdt604_validation.json`: independent artifact validation.

The exhaustive segmentation and key freezes are retained because restart
instability is the central result and cannot be reproduced from aggregate
scores alone.
