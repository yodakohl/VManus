# Cross-base opening-member synthetic preflight

Status: **FROZEN_TARGET_FREE_SHARED_MEMBER_CALIBRATION**

## Estimand

Test whether an exact first-remainder member state predicts the `D1 A1`
opening choice in a different base and a different physical folio, beyond the
fixed operation prevalence of each base/folio cell.  This is distinct from the
confirmed within-base, cross-folio `(base, onset)` result.

The preflight may read only the 1,207-row cross-base masked panel and 1,763-row
quota table.  It may not open the source STA table, a real row operation label,
the prior target JSON/report, or any event/locus context.

## Frozen predictor

For every one of the 101 eligible target cells `c=(base b, folio f)`:

1. let `q_c` be its fixed `DA / total` quota fraction;
2. train only on complete panel rows whose base is not `b` and whose physical
   folio is not `f`;
3. center every training row's binary assignment by its own cell quota;
4. for exact onset `o`, set
   `delta_o = sum(y_i - q_cell(i)) / (n_o + 8)` over that training set;
5. predict target row `i` with
   `p1_i = clip(q_c + delta_onset(i), 1e-6, 1-1e-6)` and compare it with
   `p0_i = q_c` by Bernoulli log-likelihood gain.

Average eligible rows within target cell, target cells equally within base,
and the 24 eligible bases equally for the primary score.  The 24 base means
also define positive-base count, maximum absolute contribution fraction, and
all 24 one-base deletion means.  Currier diagnostics average target-cell
scores inside A and B.  The six opaque onset-family diagnostics average target
cells inside family.  No family or onset direction is selected from real data.

## Null and pass gates

Every assignment preserves the exact `DA` count inside all 197 base/folio
cells.  The deterministic null ranks use domain
`SNOCROSS1|PREFLIGHT_NULL|base|folio|unit`.  A result passes only if all hold:

- exact upper p<=.01 and z>=3 under the complete 8,192-assignment null orbit;
- gain>=.01 nat per eligible row;
- at least 16/24 positive base means;
- maximum absolute base contribution fraction<=.15;
- every one-base deletion mean is positive;
- Currier A and B means are each>=.005;
- at least four of six onset-family means are positive;
- maximum absolute family contribution fraction<=.45.

## Synthetic calibration

At 2,048 assignments score 64 `NULL` worlds and eight worlds each of:

- `GLOBAL_SHARED`: the same deterministic onset rank in every base and folio;
- `BASE_RANDOM`: an independent onset rank for each base;
- `FOLIO_RANDOM`: an independent onset rank for each folio;
- `ONE_BASE`: the shared onset rank occurs only in one base;
- `ONE_FAMILY`: the shared onset rank occurs only in one onset family.

Plants mix `.80 * signal + .20 * unit noise` and select the highest ranks
inside each exact quota cell.  `ONE_BASE` and `ONE_FAMILY` use deterministic
world-index cycling over the full eligible inventories.  Calibration passes
only with zero of 64 null passes, at least seven of eight `GLOBAL_SHARED`
passes, and zero passes in every adversarial family.  Re-score `NULL` world 0
and `GLOBAL_SHARED` world 100 against 8,192 assignments and require unchanged
pass/fail decisions.  Missing/duplicate rows, nonbinary assignments, quota
drift, and altered eligibility must hard-stop.

## Ceiling

A preflight pass authorizes one separately specified target run.  A later
target pass could establish a shared manuscript-internal exact-member
compatibility across bases and folios.  It could not identify allomorphy,
harmony, orthography, morphology, pronunciation, wordhood, POS, syntax,
language, cipher operation, meaning, plaintext, or translation.
