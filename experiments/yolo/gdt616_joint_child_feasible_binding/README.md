# GDT616 — joint child feasible binding

Status: `NO_JOINT_CHILD_FEASIBLE_BINDING`

GDT616 repairs the exact failure exposed by GDT615: it searches the
primitive/output binding and all eight real paid locations/cards together, and
requires every unoverridden recursive child span before any mapping can enter
a full TRAIN-world search.

Both exact Stage-A solvers return UNSAT on the complete joint mapping/paid
space, and the comparison artifact binds their agreement. The corrected
post-terminal 23-group diagnostic is separately hash-bound. A second exact
diagnostic finds the nearest adjacent repair: zero through three paid-child
TRAIN-gate breaks remain UNSAT, while exactly four are SAT with all eight paid
cards and every effective TRAIN gate intact. Neither diagnosis alters the
strict decision. Stage B therefore does not run. Held, `lm_confirm`, Voynich
target data, f84, and f84r remain unopened.

Registration:

```bash
python3 experiments/yolo/gdt616_joint_child_feasible_binding/src/prepare.py
python3 experiments/yolo/gdt616_joint_child_feasible_binding/src/prepare.py --check
```

See `PREREGISTRATION.md`, `METHOD.md`, and `experiment.json`.

Terminal validation:

```bash
python3 experiments/yolo/gdt616_joint_child_feasible_binding/src/validate_result.py
```

Exact diagnostic replay, when a solver replay is desired:

```bash
python3 experiments/yolo/gdt616_joint_child_feasible_binding/src/diagnose_unsat_core.py --check
python3 experiments/yolo/gdt616_joint_child_feasible_binding/src/diagnose_relaxation.py --self-test
```

See `REPORT.md` for the decision and its deliberately narrow claim ceiling.
