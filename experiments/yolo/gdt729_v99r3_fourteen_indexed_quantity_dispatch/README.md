# GDT729 — V99R3 fourteen indexed quantity dispatch

Status: `PASS_V99R3_14_QUANTITY_READINGS__5_CARDINAL_1_INDEXED_SHARE_7_OPEN_VALUE_1_QUALITY_GRADE_0_MEASURE_0_HOLD__140_OCCURRENCES__NO_SLASH_AMBIGUITY_IN_TARGET_MEANINGS__324_ACTIVE_1248_OTHER_GLOBAL_BYTE_STABLE__SCORE_EVIDENCE_SCOPE_EXPORT_UNCHANGED__ZERO_COMPONENT_CREDIT__ALL_H0_NONE`

GDT729 replaces the fourteen named inherited `Menge/Klasse` and
`Grad-/Maßwert` whole-reading labels with one spoken default apiece. It does
not make the repeated internal pieces into a free numeral system. The
canonical result is
`artifacts/V99R3_COMPLETE_WORD_CONFIDENCE.tsv`.

Reproduce from repository root:

```bash
python3 experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch/src/run.py
python3 experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch/src/validate.py
```

See `METHOD.md`, `REPORT.md`, the exact fourteen-row source specification and
`experiment.json` for scope and limits.
