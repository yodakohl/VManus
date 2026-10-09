# GDT1311 fixed native run comparison

Read REPORT.md and the frozen NATIVE_OBSERVATION.json. One informed visual observation is not automatically reproducible handwriting truth.

Reproduce source accounting from repository root:
`PYTHONDONTWRITEBYTECODE=1 python experiments/yolo/gdt1311_f102v2_run_shape_comparison/src/run.py`

Validate source/provenance receipts:
`PYTHONDONTWRITEBYTECODE=1 python experiments/yolo/gdt1311_f102v2_run_shape_comparison/src/validate.py`

The optional `--image-dir` argument checks the three original local files named in receipts. Obtain them from the exact official URLs; image bytes are not part of the public artifact. No source normalization or new target is authorized by these commands.
