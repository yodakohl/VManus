# GDT548 — unified 145 prose reader

This experiment compiles the four final GDT542 support tiers into one exact
surface-keyed reader while preserving the GDT540 meanings and context contract.

Status: `PASS_ONE_EXACT_KEY_READER_FOR_145_PROSE_SURFACES__23_NAMED_DEFAULTS`

Primary report: `REPORT.md`

Run:

```bash
python3 experiments/yolo/gdt548_unified_145_prose_reader/src/run.py
python3 experiments/yolo/gdt548_unified_145_prose_reader/src/validate.py
python3 experiments/yolo/gdt548_unified_145_prose_reader/src/read_prose.py \
  --surface dalol --active-action CH --active-argument Y
```
