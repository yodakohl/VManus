# GDT586 — complete name-layer reader

GDT586 installs all 109 GDT585 values in the complete current reader without
inventing links between local labels and running text.

The complete edition has two page-grouped but structurally separate layers:
793 running statements and 744 local cards. Exactly two statements receive the
owner-bound values `Beschwerde` and `Heilmittel`; 107 learned names populate 89
local cards. All older GDT582 values remain available as exact rivals.

Start with [REPORT.md](REPORT.md), then use
[GDT586_COMPLETE_THIRTY_PAGE_READER.md](artifacts/GDT586_COMPLETE_THIRTY_PAGE_READER.md)
for the full reading and
[GDT586_MANUAL_CONTEXT_AUDIT.md](artifacts/GDT586_MANUAL_CONTEXT_AUDIT.md) for
the nineteen-group result.

Reproduce with:

```bash
python3 experiments/yolo/gdt586_complete_name_layer_reader/src/run.py
python3 experiments/yolo/gdt586_complete_name_layer_reader/src/validate.py
```
