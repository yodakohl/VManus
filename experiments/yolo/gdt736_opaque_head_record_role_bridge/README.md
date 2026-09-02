# GDT736 — opaque head record-role bridge

Status: `RECORD_LOCATION_X_BODY_AFFINITY_2X2_SELECTED`

GDT736 replaces the failed four-material interpretation of the modern EVA
`p/s/r/l` labels with a target-supported 2×2 record architecture:

| | body cluster A: form/state-heavy | body cluster B: materia/value-heavy |
|---|---|---|
| entry-biased | H1: paragraph/record opener | H2: line item/subentry |
| internal/final-biased | H4: internal field | H3: late internal/reference field |

The placement split is large: H1/H2 are line-first at 294/575 positions,
against 39/591 for H3/H4 (odds ratio 14.81; body+section-adjusted 16.68).
Across the same 24 bodies, the two strongest frequency-profile pairs are
H1–H4 (cosine 0.919) and H2–H3 (0.934); every other pairing is below 0.47.

The experiment supplies 1,166 occurrence contexts, a revised 24-body role
dictionary, scoped renderings for all 96 exact forms, and 24 repaired span
examples. The concrete pharmaceutical wording is an exploratory renderer,
not recovered plaintext. H1–H4 still have zero identified lexemes.

No new manuscript page was opened. The calculation reuses the inherited
179-page guarded cache; the 96 target forms occur on 141 of those pages.
`f1r`, `f84`, and `f84r` remain outside the materialized target.

Run:

```bash
python3 experiments/yolo/gdt736_opaque_head_record_role_bridge/src/run.py
python3 experiments/yolo/gdt736_opaque_head_record_role_bridge/src/validate.py
```

See [REPORT.md](REPORT.md) for the interpretation and [METHOD.md](METHOD.md)
for reproduction details.
