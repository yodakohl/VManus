# GDT1165 — q visual combination transfer

Status: `NUMERICAL_FIT_FAIL`. No translation selected.

[Report](REPORT.md), [all family results](CANDIDATE_TABLE.md), [frozen method](METHOD.md).

Reproduce the frozen run with Python and NumPy:

```sh
python3 experiments/yolo/gdt1165_q_visual_combination_transfer/src/run.py --workers 32
python3 experiments/yolo/gdt1165_q_visual_combination_transfer/src/export.py
```

The independent validator additionally needs SciPy:

```sh
python3 experiments/yolo/gdt1165_q_visual_combination_transfer/src/validate.py
```

An accounting PASS cannot supersede the numerical test failure or establish meaning. All inputs were already exposed; no reserve use.
