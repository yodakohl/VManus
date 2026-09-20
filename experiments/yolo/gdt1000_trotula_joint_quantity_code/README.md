# GDT1000 — complete Trotula recipes with a shared quantity construction

See METHOD.md, PREREGISTRATION.md, SOURCE.json under src, and REPORT.md after
execution. Inputs and outputs are hash-bound by experiment.json. Required
Python packages: cvc5==1.3.4 for run.py, z3-solver==4.15.3.0 for validate.py.

Run the source-only checks before registration, then the complete experiment:

```bash
python3 experiments/yolo/gdt1000_trotula_joint_quantity_code/src/run.py --fixtures
python3 experiments/yolo/gdt1000_trotula_joint_quantity_code/src/validate.py --selftest
python3 experiments/yolo/gdt1000_trotula_joint_quantity_code/src/run.py
python3 experiments/yolo/gdt1000_trotula_joint_quantity_code/src/validate.py
```

The whole pair table is gzip-compressed with a deterministic zero timestamp.
Its integer indices refer to PARAGRAPH_CASES.json and CANDIDATES.tsv. No guessed
meaning is promoted to a confirmed translation by a satisfiable code equation.
