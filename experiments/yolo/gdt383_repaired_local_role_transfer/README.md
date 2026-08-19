# GDT383 — repaired multi-resolution local-role transfer

GDT383 first revalidates a repaired source→post-pivot instrument on the frozen
GDT382 readable positive controls.  Voynich access is conditional: if Stage A
fails, no target file may be read.

```bash
python src/freeze_stage_a.py
python src/validate_stage_a_freeze.py
python src/run_stage_a.py
python src/validate_stage_a.py
```

Stage B requires a separately published target freeze after, and only after,
the Stage A authorization gate passes.
