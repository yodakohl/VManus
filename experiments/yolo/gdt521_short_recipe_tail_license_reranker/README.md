# GDT521 — short recipe tail license reranker

Status: `PASS_SHORT_RECIPE_TAIL_LICENSE_RERANKER`

GDT521 adds a type-balanced order-five atom model to GDT520. A candidate is
judged from at most four preceding components; no full surface exception is
stored. This restores `psheody → P+SH+E+O+D_ADDR+Y` while retaining
`shckheody → SH+CH+K+E+O+DY`.

The old four-fold rehearsal reaches 1,090 rank-one / 1,418 top-five with rank
sum 2,118. The current 159-form deck reaches 140 rank-one and rank sum 189.

```bash
python3 experiments/yolo/gdt521_short_recipe_tail_license_reranker/src/run.py
python3 experiments/yolo/gdt521_short_recipe_tail_license_reranker/src/validate.py
python3 experiments/yolo/gdt521_short_recipe_tail_license_reranker/src/align_surface.py \
  --surface NEUE_FORM --domain PROSE_STREAM --top 5
```
