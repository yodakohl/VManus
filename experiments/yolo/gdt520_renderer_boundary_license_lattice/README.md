# GDT520 — renderer boundary license lattice

Status: `PASS_RENDERER_BOUNDARY_LICENSE_LATTICE`

GDT520 adds two small decisions to GDT519's visible-stem transducer:

1. when two candidates otherwise fit similarly, prefer the one using fewer
   already licensed renderer segments;
2. price each visible character cut from old pair and four-character-window
   usage instead of assuming that every plausible character is a separate
   component.

The selected working model improves the rotating old-form rehearsal from
1,082 to 1,089 rank-one recoveries and the current 159-form deck from 138 to
139. See `REPORT.md` for the interpretation and the remaining `...eody`
ambiguity.

Rebuild and validate:

```bash
python3 experiments/yolo/gdt520_renderer_boundary_license_lattice/src/run.py
python3 experiments/yolo/gdt520_renderer_boundary_license_lattice/src/validate.py
```

Use the live intake command:

```bash
python3 experiments/yolo/gdt520_renderer_boundary_license_lattice/src/align_surface.py \
  --surface NEUE_FORM --left-recipe SH+E+Y --right-recipe K+O+DY \
  --domain PROSE_STREAM --top 5
```
