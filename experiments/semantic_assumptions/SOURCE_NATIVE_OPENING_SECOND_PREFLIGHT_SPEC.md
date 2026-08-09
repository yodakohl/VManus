# Second-member incremental synthetic preflight

Status: **FROZEN_TARGET_FREE_LONGER_TEMPLATE_CALIBRATION**

## Estimand

Among the 639 prespecified eligible rows, test whether the exact second
remainder member improves held-physical-folio prediction of the `DA`/literal
`qo` construction after both the complete coarse remainder and exact first
member are fixed.  This cannot be satisfied by rediscovering the confirmed
first-onset orthotactic relation.

For each held folio, train on all other folios.  Let baseline be
`(base_id, onset_id)` and refinement be `(base_id, onset_id, second_id)`.
With symmetric base prior `.5`, set
`p0=(DA_baseline+.5)/(n_baseline+1)`.  With refinement strength four, set
`p1=(DA_refinement+4*p0)/(n_refinement+4)`.  Score Bernoulli
`log P(y|p1)-log P(y|p0)` only on the frozen eligible rows.  Average eligible
rows within physical folio and then 41 folios equally.

Also aggregate scored row gains equally within each of the 16 eligible bases.
The pass requires exact upper p<=.01, z>=3, gain>=.01 nat/row, at least 28/41
positive folios, maximum absolute folio share<=.15, every folio deletion
positive, Currier A and B folio means each>=.005, at least 10/16 positive base
means, maximum absolute base share<=.25, and every base deletion positive.

## Synthetic controls

Preserve every exact `DA` quota in all 197 base/folio cells.  At 2,048 null
assignments score 64 `NULL` worlds and eight worlds each of:

- `GLOBAL_SECOND`: one stable deterministic rank for each exact
  `(base, onset, second)` refinement across folios;
- `BASELINE_ONLY`: rank depends only on `(base, onset)` and must not create a
  second-member increment;
- `ONE_FOLIO`: refinement signal only on one folio;
- `FOLIO_RANDOM`: independently remapped refinement signal on every folio;
- `ONE_BASE`: refinement signal only in one base.

Plants use `.80 * signal + .20 * unit noise` and select the exact quota within
each cell.  Calibration passes only with zero of 64 null passes, at least seven
of eight global-second passes, and zero passes in every adversarial family.
Re-score null world 0 and global-second world 100 against 8,192 assignments and
require unchanged decisions. Missing/duplicate rows, nonbinary labels, quota
drift, and changed eligibility must hard-stop.

The preflight may read only the frozen masked panel, quota table, validated
capacity, this specification, core, and runner. It may not open the source STA
table, prior target artifacts, real operation labels, or a target output.

## Ceiling

A pass authorizes one separately frozen real target.  A later target pass could
establish a longer transcription-template dependency beyond the immediate
`qo` onset relation.  It could not establish morphology, pronunciation,
wordhood, POS, syntax, language, cipher operation, meaning, plaintext, or
translation.
