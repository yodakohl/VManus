# GDT756 — `ychor` line frame and complete candidate rendering

GDT756 tests whether GDT755's `ychor=nimm` lead is better read as the
late-medieval continuation marker `Item=ferner/ebenso`. It follows all thirteen
exact `ychor` lines, compares their bodies with 247 closely matched continuation
lines, and gives every one of the 71 following token positions a concise
complete-form candidate plus two rivals.

Run:

```bash
python3 experiments/yolo/gdt756_ychor_line_frame_content_slots/src/run.py
python3 experiments/yolo/gdt756_ychor_line_frame_content_slots/src/validate.py
```

Primary result: `REPORT.md`. Full line reader:
`artifacts/GDT756_YCHOR_FRAME_READER.md`.
