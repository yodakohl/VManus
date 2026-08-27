# GDT577 — interrupted modifier attachment topology

Status: `PASS_62_INTERRUPTED_GROUPS__125_SLOTS__75_EXISTING_ATTACHMENTS_REPLAYED__50_EXPLORATORY_HEAD_CANDIDATES__5_TOPOLOGIES__ONE_RENDERER_HISTORY_CONFLICT__ZERO_SLOT_COLLAPSE`

GDT577 reconnects all 125 written slots in GDT575's 62 interrupted
same-root groups to a visible action, an active context action, or one explicit
sequence carrier. It reproduces all 75 previously fixed focus attachments and
marks the 50 O/D_ADDR attachments as exploratory voice candidates.

Run:

```bash
python3 experiments/yolo/gdt577_interrupted_modifier_attachment_topology/src/run.py
python3 experiments/yolo/gdt577_interrupted_modifier_attachment_topology/src/validate.py
```

The primary result is [REPORT.md](REPORT.md). This pass is an atlas, not yet a
rewrite of the complete readable edition.
