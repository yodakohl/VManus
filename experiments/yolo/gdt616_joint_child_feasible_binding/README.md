# GDT616 — joint child feasible binding

Status: `REGISTERED_UNSCORED`

GDT616 repairs the exact failure exposed by GDT615: it searches the
primitive/output binding and all eight real paid locations/cards together, and
requires every unoverridden recursive child span before any mapping can enter
a full TRAIN-world search.

The fail-fast recursive bound does not commit its SAT witness. W0 is selected
over the complete bound-feasible space, with no raw-support objective. Three
complete TRAIN worlds must be hash-committed before held or `lm_confirm` is
opened. Voynich target data and f84/f84r remain forbidden.

Registration:

```bash
python3 experiments/yolo/gdt616_joint_child_feasible_binding/src/prepare.py
python3 experiments/yolo/gdt616_joint_child_feasible_binding/src/prepare.py --check
```

See `PREREGISTRATION.md`, `METHOD.md`, and `experiment.json`.
