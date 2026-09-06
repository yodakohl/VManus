# GDT858: held-face versus held-leaf audit

963/963 primary GDT808 folds reconstruct exactly. In 855, training retains
opposite-face events of the held physical leaf (505/569 L; 350/394 DY).
Thus these are face-held, not whole-leaf-held, folds. No score or refit claim.

See REPORT.md and METHOD.md. Reproduce:

```
python3 experiments/yolo/gdt858_folio_holdout_unit_audit/src/run.py
python3 experiments/yolo/gdt858_folio_holdout_unit_audit/src/validate.py
python3 experiments/yolo/gdt858_folio_holdout_unit_audit/src/run.py --check
python3 experiments/yolo/gdt858_folio_holdout_unit_audit/src/bind.py
```

Source access is restricted to the registered selector-first metadata
projections. The validator independently repeats both guarded projections.
