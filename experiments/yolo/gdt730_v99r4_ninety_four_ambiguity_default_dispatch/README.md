# GDT730 — V99R4 ninety-four ambiguity-default dispatch

Status: `PASS_V99R4_94_AMBIGUOUS_GLOBAL_WHOLES__1039_OCCURRENCES__TECHNICAL_SELECTOR_95_ROWS_1050_OCCURRENCES__CPHOL_LEXICAL_FALSE_POSITIVE__MAIN_AND_CONTEXT_DEFAULTS_AMBIGUITY_FREE__GDT730_PROVENANCE_APPENDED__SCORE_CONFIDENCE_EVIDENCE_SCOPE_EXPORT_SPAN_STRUCTURE_ACTION_UNCHANGED__ZERO_COMPONENT_CREDIT`

GDT730 gives one speakable German default to every genuinely ambiguous global
whole reading selected from V99R3. The complete canonical result is
`artifacts/V99R4_COMPLETE_WORD_CONFIDENCE.tsv`; confidence and positive and
negative evidence remain attached to every row.

Reproduce from repository root:

```bash
python3 experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch/src/run.py
python3 experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch/src/validate.py
```

See `METHOD.md`, `REPORT.md`, the explicit 94-row source specification and
`experiment.json` for the exact scope and limits.
