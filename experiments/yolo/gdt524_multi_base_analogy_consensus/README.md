# GDT524 — multi-base analogy consensus

Status: `PASS_TWO_INDEPENDENT_BASE_ANALOGY_CONSENSUS`

GDT524 lets two independent old surface analogies reinforce the same candidate
recipe. Independence means both a different old base surface and a different
visible-to-atom edit channel; two near-duplicates of one edit do not count
twice.

On the 159-form current deck this corrects `kchody` and `ld` without losing a
previous rank-one decision (142 to 144). The rotating old-form rehearsal also
gains two rank-one hits (1,096 to 1,098).

```bash
python3 experiments/yolo/gdt524_multi_base_analogy_consensus/src/run.py
python3 experiments/yolo/gdt524_multi_base_analogy_consensus/src/validate.py
python3 experiments/yolo/gdt524_multi_base_analogy_consensus/src/align_surface.py \
  --surface kchody --page f66r --domain LOCAL_RECORD --top 5
```
