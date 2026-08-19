# GDT384

Comparator-only calibration of role-specific relational consequences after the
GDT383 generic-future failure.

```bash
python src/freeze_stage_a.py
python src/validate_stage_a_freeze.py
GDT384_PCEEC2_DIR=/path/to/pceec2 python src/build_relational_oracle.py
python src/run_stage_a.py
python src/finalize_stage_a.py
python src/validate_stage_a.py
```

Voynich access is forbidden unless the complete Stage-A result separately
authorizes a target freeze.
