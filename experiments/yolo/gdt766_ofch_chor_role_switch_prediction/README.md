# GDT766 — `ofch` nominal class and `chor` whole-word role switch

Status: `PARTIAL`, independently rebuilt and validated with 5,294 checks.

GDT766 compares 43 exact occurrences of 25 complete words containing `ofch`
with 191 exact occurrences of `chor`, `pchor`, `schor` and `lchor`. The result
selects a portable nominal drug/preparation analogy for the observed `ofch`
wholes and a role-switched learned-whole model for the four `chor` forms.

The deliberately concrete renderer retains flower readings at C0/C1, but no
substring meaning is exported. Five complete cached lines (46 tokens) receive
explicit defaults. The four same-line reproductive contacts remain valid
acquisition rows but are not score-ready evidence.

Run:

```bash
python3 experiments/yolo/gdt766_ofch_chor_role_switch_prediction/src/run.py
python3 experiments/yolo/gdt766_ofch_chor_role_switch_prediction/src/validate.py
```

See `METHOD.md`, `REPORT.md`, `PREREGISTRATION.md` and `experiment.json`.
