# GDT434 — forty-nine-card intake reader

Status: `EXECUTABLE_49_CARD_INTAKE_READER_WITH_SEPARATE_NARROW_APPENDIX`

This experiment turns the prospective component deck into one usable intake
reader. It accepts an already segmented recipe such as `AL+AIN`, matches that
exact key, and returns an observed reading, a future-card reading, a narrow
lookup warning, or a stop.

Run it with:

```bash
python3 experiments/yolo/gdt434_forty_nine_card_intake_reader/src/read_recipe.py \
  --recipe AL+AIN --register BIOLOGICAL
```

See [REPORT.md](REPORT.md), [METHOD.md](METHOD.md), and
[FORTY_NINE_CARD_INTAKE_SHEET.md](artifacts/FORTY_NINE_CARD_INTAKE_SHEET.md).
