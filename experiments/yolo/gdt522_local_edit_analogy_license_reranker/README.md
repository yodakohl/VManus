# GDT522 — nearest local-edit analogy license

Status: `PASS_NEAREST_LOCAL_EDIT_ANALOGY_LICENSE`

GDT522 learns reusable one-local-change correspondences between old visible
forms and their component recipes. It compares a new surface only with its
nearest old deletion-neighbour and scores the conditional mapping of the
inserted visible block to an inserted atom block. Equal recipes explicitly
learn visible-but-null insertions.

The selected light reranker preserves all 140 current GDT521 top-one hits and
adds `dcheol → D_ADDR+CH+E+O+L` and `dyky → D_ADDR+Y+K+Y`. The old four-fold
rehearsal moves from 1,090 to 1,096 rank-one hits.

```bash
python3 experiments/yolo/gdt522_local_edit_analogy_license_reranker/src/run.py
python3 experiments/yolo/gdt522_local_edit_analogy_license_reranker/src/validate.py
python3 experiments/yolo/gdt522_local_edit_analogy_license_reranker/src/align_surface.py \
  --surface NEUE_FORM --domain PROSE_STREAM --top 5
```
