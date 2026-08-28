# GDT602 — blind Naibbe-key recovery after segmentation

Status: `NAIBBE_KEY_RECOVERED_CONDITIONAL_ON_ORACLE_SEGMENTATION`.

GDT602 recovers 52,626/52,641 control characters without giving the optimizer
the aligned plaintext or published surface-to-letter table. The result is
conditional on oracle U/P/S segmentation and is therefore a solved key-search
subproblem, not an end-to-end cipher solution.

See `PREREGISTRATION.md`, `METHOD.md`, `REPORT.md`, and `experiment.json`.
