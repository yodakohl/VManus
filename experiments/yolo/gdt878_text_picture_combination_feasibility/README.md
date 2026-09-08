# GDT878 — text-picture combination feasibility

Status: `REGISTERED_UNSCORED`.

This package validates the source and observation contract for two disjoint
native branches. It does not acquire images, interpret text, or decide a
meaning. Root-owned `SOURCES.json`, `ROOT_OBSERVATION.json`, and
`GEOMETRY_B_OBSERVATION.json` are required before running it.

```bash
python3 experiments/yolo/gdt878_text_picture_combination_feasibility/src/run.py
python3 experiments/yolo/gdt878_text_picture_combination_feasibility/src/validate.py
```

The validator checks protocol hashes, fixed anchors, branch separation, scope
exclusions, and uncertainty. It cannot independently verify native vision.
