# GDT790 — panel-owner image grammar overlay

Status: `PASS__3_PAGES__10_IMAGE_PANELS__13_RECORDS__123_PROSE_LINES__940_PROSE_TOKENS__27_LABEL_LOCI__28_LABEL_TOKENS__10_EXACT_LABEL_PROSE_EDGES__9_MULTI_CHARACTER_EDGES__PANEL_OWNER_OVERLAY__ZERO_TOKEN_MEANING_CHANGES__ZERO_PREFIX_EXPORT`

GDT790 adds the visible panel as a silent owner above the existing text
grammar for f77r, f82r and f83r. It produces a complete image-aware structural
reader without converting the drawings into invented verbs or assigning a
single figure to an ordinary prose word by proximity.

Start with [REPORT.md](REPORT.md), then inspect the complete
[image-aware record reader](artifacts/GDT790_IMAGE_AWARE_RECORD_READER.md) and
the [manual image-grammar audit](artifacts/GDT790_MANUAL_IMAGE_GRAMMAR_AUDIT.md).

Run:

```bash
python3 experiments/yolo/gdt790_panel_owner_image_grammar_overlay/src/run.py
python3 experiments/yolo/gdt790_panel_owner_image_grammar_overlay/src/validate.py
```
