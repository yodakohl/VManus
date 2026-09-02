# GDT732 — v99r5 grade frame spoken renderer

Status: `PASS_175_GRADE_READINGS_2431_LICENSED_POSITIONS__162_GLOBAL_2401_PLUS_13_ACTIVE_30__1784_TARGET_ACTIVE_SURFACE_LEAK_CONTROLS__75_DIRECT_ROWS_1748_POSITIONS__100_NEUTRAL_ROWS_683_POSITIONS__ZERO_TARGET_GRADE_FRAMES__4752_V48_BASELINE_RESIDUALS_4692_ACTIVE_OUTSIDE_EXACT_PLUS_52_SUPERSEDED_EXACT_PLUS_8_ALIAS_MERGE__V99R4_SEMANTIC_DICTIONARY_BYTE_STABLE__NO_NEW_PAGE`

GDT732 turns the audible analytical grade wording in all 175 licensed V99R4
grade readings into a shorter spoken-state layer while retaining stage,
workflow closure, modality, evidence, confidence and exact dispatch scope as
separate fields. It changes 2,431 licensed positions and no other token cell.

The target-only full-cache projection also exposes 4,752 older grade-bearing
V48 cells. Of these, 4,692 lie outside current exact active scope, 52 are
already superseded at exact V99 positions, and eight are contextual
alias/merge cells. They remain explicitly classified rather than silently
presented as finished.

Reproduce from repository root:

```bash
python3 experiments/yolo/gdt732_v99r5_grade_frame_spoken_renderer/src/run.py
python3 experiments/yolo/gdt732_v99r5_grade_frame_spoken_renderer/src/validate.py
```

See `METHOD.md`, `REPORT.md`, the explicit policy deck and `experiment.json`
for the exact scope and limits.
