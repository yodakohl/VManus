# GDT622 — Clm 667 temperament codebook

Status: `CONCRETE_COMPOSITIONAL_WORKING_TRANSLATION_V1`

GDT622 tests a concrete historical model for the Herbal pages: a learned drug
or plant name can coexist with a very short compositional code for hot/cold,
moist/dry, and degree. BSB Clm 667 supplies a real 1481–1490 comparator with
exactly that architecture. The current Voynich reader is:

`qo- + k/t + ch/sh + ending`, with working values
`k=hot`, `t=cold`, `ch=moist`, `sh=dry`.

This produces four target-span readings and one visual label hypothesis. The
name carriers and attachment between a page heading and a later code remain
hypotheses, not decoded lexemes.

Primary result: `REPORT.md`.

Rebuild and validate:

```bash
python3 experiments/yolo/gdt622_clm667_temperament_codebook/src/run.py
python3 experiments/yolo/gdt622_clm667_temperament_codebook/src/validate.py
```
