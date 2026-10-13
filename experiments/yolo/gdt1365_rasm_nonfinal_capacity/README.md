# GDT1365 — Rasm positional capacity

Status: `FIXED_RASM_RENDERING_EXCLUDED_FULL`.

See REPORT.md for source and native claims separately. Reproduce:

```
python experiments/yolo/gdt1365_rasm_nonfinal_capacity/src/fetch_source.py
python experiments/yolo/gdt1365_rasm_nonfinal_capacity/src/source_check.py
python experiments/yolo/gdt1365_rasm_nonfinal_capacity/src/run.py
python experiments/yolo/gdt1365_rasm_nonfinal_capacity/src/validate.py
```

Only pinned public MIT code is fetched; corpus/data APIs are forbidden by the
source checker. No private or bundled edition data are downloaded.
