# GDT831 reproducible observation control

The exact design is PREREGISTRATION.md and src/SPEC.json. Native source hashes
and 24 tile bounds are in src/SOURCES.json and src/TILES.json. Two separate
visual annotators supply src/ANNOTATIONS_CAL.tsv and src/ANNOTATIONS_HELD.tsv;
their reviews record coordinate selection and uncertainty. A point's
source coordinate is (tile.x0+x,tile.y0+y). No source image is embedded here.

With Python3, NumPy and Pillow installed, run from repository root:

```sh
python3 experiments/yolo/gdt831_annotated_ink_paper_control/src/test_measurement.py
python3 experiments/yolo/gdt831_annotated_ink_paper_control/src/run.py --calibrate --fetch
python3 experiments/yolo/gdt831_annotated_ink_paper_control/src/run.py --evaluate --fetch
python3 experiments/yolo/gdt831_annotated_ink_paper_control/src/validate.py --cache-dir .cache/gdt830_native
```

All image-reading commands support --cache-dir. Default native cache is
.cache/gdt830_native; --fetch retrieves only the four hash-bound official
source images as needed. The first two real-data invocations are separate so
CALIBRATION.json exists before any held score.

`run.py --check --fetch` replays source pixels and compares artifacts without
rewriting them. The independent validator checks its stated coverage;
software PASS is distinct from the experiment's scientific outcome.
Inspection plates may be recreated with src/inspect_tiles.py. They repeat
source pixels exactly and add ticks/rings only as explicitly marked review
aids. The native tile RGB hash is the portable evidence binding; historical
display PNG hashes also depend on the installed rendering font/library.
