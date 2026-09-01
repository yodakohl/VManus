# GDT731 — V99R4 occurrence and passage impact

Status: `PASS_94_SURFACES_1039_POSITIONS_911_LINES__351_COMPLETE_LINES__50_TARGET_DENSE_PASSAGES__GDT696_OVERLAYS_BYTE_STABLE__CACHED_DEFAULT_IMPACT_ONLY__NO_POLISHED_TRANSLATION_OR_NEW_PAGE`

GDT731 projects all 94 V99R4 defaults onto every one of their 1,039 cached
V48 occurrences. It publishes exact token and line deltas, 351 affected
complete lines, a 50-passage reader and a ranked census of the abstraction
that still prevents polished prose.

Reproduce from repository root:

```bash
python3 experiments/yolo/gdt731_v99r4_occurrence_passage_impact/src/run.py
python3 experiments/yolo/gdt731_v99r4_occurrence_passage_impact/src/validate.py
```

See `METHOD.md`, `REPORT.md`, the blocker-rule deck and `experiment.json` for
the exact scope and limits.
