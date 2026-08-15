# GDT096 — frozen layout-channel transfer

Freeze GDT095's exact `base|edge|ground|level` position vocabulary and its ten
representation grid. Train only on the 83 UNHEDGED section-P plant labels and
score all 35 HEDGED labels without target refitting. For every target, exclude
its complete physical folio from training. The primary frozen representation
is exact PAGE_HOST×WRAPPER; other representations are declared sensitivities.

Use the inherited K=5/shrinkage-4 neighbor rule. The baseline is training
prevalence outside the target folio. Enumerate every target-label assignment
that preserves the positive count within each physical folio (1,872 worlds)
and maximize over all ten reported representations. HEDGED is an archived
annotation-quality stratum, not a pristine holdout. No semantic role is tested.
