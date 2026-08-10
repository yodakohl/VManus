# LRG008 target-blind calibration v2 amplitude amendment

Status: `FROZEN_TARGET_BLIND_SYNTHETIC_V2`.

V1 is an independently reconstructed pretarget power stop: 0/64 null and 0/8
for every negative family passed, but distributed plants passed only 6/8 at
amplitude .60 and 4/8 at .35. The failures were the already frozen z and
small-section material gates, not false-positive leakage.

V2 changes only:

- `DISTRIBUTED_FULL` amplitude `.60 -> 1.00`;
- `DISTRIBUTED_REDUCED` amplitude `.35 -> .75`; and
- association amplitude `.60 -> 1.00` in `ONE_FOLIO`, `ONE_ROLE`,
  `ONE_SECTION`, `ONE_PARITY`, `ONE_PAGE`, `FOLIO_RANDOM_SIGN`, and
  `REVERSED` adversaries.

The 64 nulls, Gaussian draws, seeds, exact quotas, 8,192 assignment rows,
rank transform, hierarchy, all nine statistical thresholds, world counts,
metadata-only controls, malformed controls, invariances, target isolation,
and claim ceiling are byte-for-byte or formula-for-formula unchanged from v1.

V2 passes only with 0/64 null, 8/8 at both distributed strengths, 0/8 in all
nine negative families, and every integrity gate. It supplies no manuscript
association or interpretation and may authorize only a separately registered,
committed, hash-frozen aggregate target.
