# One-shot exact-member onset target

Status: **FROZEN_ONE_TIME_REAL_OPERATION_LABEL_TARGET**

## Target

Join the real `NONE`/`DA` operation label to exactly the validated 1,207-row
masked onset panel.  Require 892 `NONE`, 315 `DA`, and every one of the 197
base/physical-folio quota counts exactly.  Derive labels only from the frozen
longest family-opening split; do not inspect a result before this specification
and runner are published.

Use the calibrated statistic unchanged:

- score only the 1,141 rows whose exact base/onset pair occurs off the held
  physical folio;
- compare leave-folio-out base-only `p_b=(DA_b+.5)/(n_b+1)` with
  base/onset `p_bo=(DA_bo+4*p_b)/(n_bo+4)`;
- average Bernoulli log-likelihood gain within held folio and then equally
  across all 59 folios;
- use the exact 8,192-assignment `PREFLIGHT_NULL` quota-preserving orbit.

Pass only with upper p<=.01, z>=3, gain>=.01 nat/eligible row, at least 36/59
positive folios, maximum absolute folio fraction<=.15, every one-folio deletion
mean positive, and Currier A/B means each>=.005.  No feature, smoothing,
threshold, subgroup, register, null, or direction may change after execution.

## Decision and ceiling

A pass establishes that exact first-remainder STA member identity carries a
transferable manuscript-internal constraint on selection of the dominant
`D1 A1` opening beyond the coarse family remainder.  This is compatible with
allomorphy, harmony, orthography, or another symbolic compatibility rule, but
chooses none of them.  A failure rejects this first-member compatibility model
at the frozen resolution while retaining the exact `D1 A1 + remainder`
construction.

Neither outcome establishes detachment, morphology, pronunciation, wordhood,
part of speech, syntax, language, cipher operation, meaning, plaintext, or
translation.  Store one aggregate score and digests only—no row label, locus,
page, remainder identity, or event context.
