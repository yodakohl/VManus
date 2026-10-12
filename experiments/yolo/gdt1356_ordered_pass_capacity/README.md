# GDT1356 — Ordered-pass capacity

See [REPORT.md](REPORT.md) for the result and [PREREGISTRATION.md](PREREGISTRATION.md) for the fixed contract.

Run source-free checks with `python src/run.py --controls`, native calculation with `python src/run.py`, and independent witness verification with `python src/validate.py` from this directory. Python 3 and z3-solver 4.15.3 were used. Timed feasibility search may choose different upper witnesses; the validator verifies the recorded certificates without relying on solver optimality.
