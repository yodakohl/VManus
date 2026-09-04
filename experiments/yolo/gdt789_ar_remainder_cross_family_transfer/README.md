# GDT789 — `ar` remainder cross-family transfer

Status: `PARTIAL__285_RAW_FORMS__1698_RAW__225_EXACT_FORMS__1348_EXACT__47_ROBUST_AR_OR_PREFIXES__SUPPORT_ADD_BOTH_7_OF31__HISTORICAL_EXCLUSION_8_OF31__RN12_0_OF7__RN23_0_OF6__BARE_AR_ANTEIL__WHOLE_ONLY__285_DEFAULTS__ZERO_COMPONENT_EXPORT__ZERO_NEW_RENDERER_LICENSE`

GDT789 tests whether the useful complete whole `ar=Anteil` behaves as a
portable semantic remainder inside complete `Xar` surfaces.  It excludes the
longer `*dar` ending from the target family, uses 47 robust complete `Xar/Xor`
pairs, and keeps the GDT788 four-tail lattice as reference rather than scoring
it again.

The result is mixed but decisive for the renderer: replacing `Xor` by the
profile estimate `Xor + ar - or` helps against `Xor` alone in 21/31 support
types, yet defeats both `Xor` and learned-whole controls in only 7/31.  An
a mechanically defined, partly overlapping 31-type historical-exclusion
cohort gives 8/31, and neither R/N level grid transfers. `ar=Anteil` therefore
survives as a replaceable complete-word default; longer forms remain
complete-whole cards with no free `ar` export.

Run:

```bash
python3 -B experiments/yolo/gdt789_ar_remainder_cross_family_transfer/src/run.py
python3 -B experiments/yolo/gdt789_ar_remainder_cross_family_transfer/src/validate.py
```

See `METHOD.md`, `PREREGISTRATION.md`, `REPORT.md`, and `experiment.json`.
