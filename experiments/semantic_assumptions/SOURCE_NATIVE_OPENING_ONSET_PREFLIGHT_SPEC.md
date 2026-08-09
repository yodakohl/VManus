# Opening-onset compatibility preflight

Status: **FROZEN_TARGET_FREE_SYNTHETIC_CALIBRATION**

## Fixed statistic

Use the validated 1,207-row label-masked onset panel and the existing 197
family-remainder/physical-folio quota cells.  Score only the 1,141 rows whose
exact `(base_id, onset_id)` pair occurs on another physical folio.

For each held folio and each label assignment:

1. train on every other folio;
2. estimate the base-only probability
   `p_b = (DA_b + 0.5) / (n_b + 1)`;
3. estimate the onset-adjusted probability
   `p_bo = (DA_bo + 4*p_b) / (n_bo + 4)`;
4. score held eligible rows by the mean Bernoulli log-likelihood gain of
   `p_bo` over `p_b`;
5. average the 59 held-folio scores with equal folio weight.

The primary statistic is this equal-folio mean gain in natural-log units per
eligible row.  Also record positive folios, maximum absolute folio fraction,
minimum leave-one-folio-out mean, and equal-folio Currier A/B means.

## Exact conditional null

Every assignment preserves the exact `DA` count inside each of the 197 frozen
base/folio quota cells.  Rows receive deterministic SHA-256/SplitMix64 ranks;
the top quota count is labeled `DA`.  The primary tail is upper, with the
observed assignment included in the denominator.  Use 2,048 assignments for
the calibration grid and 8,192 for frozen target-size decision checks.

A statistic passes only if all hold:

- upper p <= .01 and z >= 3;
- observed gain >= .01 nat/eligible row;
- at least 36/59 folio gains are positive;
- maximum absolute folio contribution fraction <= .15;
- every one-folio deletion mean is positive;
- Currier A and B equal-folio means are each >= .005.

## Frozen calibration grid

All synthetic labels preserve the real quota cells.

- 64 `NULL` worlds: unit-specific deterministic noise only;
- 8 `GLOBAL_ONSET` worlds: one base/onset ranking shared across folios;
- 8 `ONE_FOLIO` worlds: that ranking applies on one folio only;
- 8 `FOLIO_RANDOM` worlds: independent onset rankings by folio;
- 8 `ONE_BASE` worlds: the shared ranking applies within one base only.

Signal strength is fixed at .80 in `.80*signal + .20*unit_noise`.  Calibration
passes only with 0/64 null passes, at least 7/8 global-onset passes, and zero
passes for every adversarial family.  `NULL` world 0 and `GLOBAL_ONSET` world
100 must keep the same decisions at 8,192 assignments.

## Isolation and ceiling

The calibration runner may open only the masked onset panel, aggregate quota
table, capacity result/validation, this spec, and its own core/source.  It must
not open the manuscript source, the member-audit source join, the hidden real
operation labels, or any real target artifact.  A pass authorizes independent
reconstruction and then one separately frozen target only.  It establishes no
detachment, allography, morphology, sound, wordhood, syntax, language, cipher
operation, meaning, plaintext, or translation.
