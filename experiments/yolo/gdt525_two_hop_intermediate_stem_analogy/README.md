# GDT525 — two-hop intermediate-stem analogy

Status: `PASS_K_BASE_Y_THEN_E_STEM_CLOSURE`

GDT525 composes two old local edits through one explicit intermediate stem. A
broad two-hop bonus is too noisy. The retained narrow card is the repeated
K-base chain `right y -> Y`, then `inner e -> E`.

It changes exactly three current surfaces. Against inherited GDT516 defaults
the 159-form top-one count moves 144 to 145. The family-consistent working
edition also repairs the explicitly provisional `kcheody` parse and moves 143
to 146. The old four-fold metrics remain exactly unchanged.

```bash
python3 experiments/yolo/gdt525_two_hop_intermediate_stem_analogy/src/run.py
python3 experiments/yolo/gdt525_two_hop_intermediate_stem_analogy/src/validate.py
python3 experiments/yolo/gdt525_two_hop_intermediate_stem_analogy/src/align_surface.py \
  --surface kcheody --page f66r --domain PROSE_STREAM --top 5
```
