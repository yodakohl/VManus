# GDT905 — constructive complete-passage candidates

See [METHOD.md](METHOD.md) for the sole protocol. Status: registered exploratory
construction; no control pass or manuscript meaning.

Use the unchanged GDT892 source acquisition to prepare a cache matching all
REFERENCE.json hashes. Set GDT905_CACHE to that directory and GDT905_WORK to
a disposable working directory. Run src/run.py with --cache-dir and --work-dir,
first --stage intake, then --stage scan, then --stage fit. The initial execution
uses --stop-at-utc 2026-09-10T06:17:00+00:00; reproduction may omit that historical
wall-clock deadline while retaining the registered per-paragraph limits.
