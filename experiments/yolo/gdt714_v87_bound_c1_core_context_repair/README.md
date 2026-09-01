# GDT714 — V87 bound-C1 core/context repair

Status: `PASS_V87_18_BOUND_C1_READINGS_REVISED__18_TARGET_POSITIONS_12_PAGES__1_KEO_R_ONE_SHOT_SPAN__7_W0_135_W1_163_W2_19_W3__91_WEAK_READINGS_REMAIN__ALL_H0_NONE`

GDT714 replaces eighteen overpacked C1 working cores with compact state,
quantity, portion and state readings. It also installs the already admitted
GDT678 f7r.2 `keo r -> heiße Portion` decision as a nonexportable one-shot
renderer that actually consumes both source positions, while preserving the
global `r = Wurzel` working card outside that span.

Start with `REPORT.md`. The canonical dictionary is
`artifacts/V87_COMPLETE_WORD_CONFIDENCE.tsv`; the compact eighteen-row change
set and one-row boundary decision sit beside it. Rebuild with
`python3 src/run.py` and validate with `python3 src/validate.py` from this
directory, or use the commands in `experiment.json` from the repository root.
