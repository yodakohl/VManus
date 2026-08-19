# GDT382 — Voynichification methodology audit

This experiment is a comparator-only positive-control audit.  It asks whether
the GDT376–381 style methodology can recover known hidden functional classes
after readable medieval corpora are converted into a deliberately composite,
Voynich-like observation layer.

The experiment never reads or scores Voynich data.  In particular, no f84
file, row, image, transcription, or formal payload is an input.

Run order:

```bash
python src/freeze_gdt382.py
python src/validate_gdt382_freeze.py
python src/run_gdt382.py
python src/validate_gdt382.py
```

The encoder and recovery design are committed before `run_gdt382.py` may read
the hidden oracle.
