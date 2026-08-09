# Endpoint-free source-group interior-position test

Status: **REGISTERED_TARGET_UNOPENED**

## Representation and model

Use the 19,203-row masked interior panel. The target is the official STA-family
sequence after deleting the first and last family from each complete source
group. This removes the already-confirmed endpoint signal completely.

Fit separate distributions by Currier and exact original group length 3--11.
All use symmetric Dirichlet alpha .5:

- `K1`: one exchangeable distribution across the interior;
- `FIXED_K`, K=2..5: deterministic relative interior bins
  `min(K-1, floor(K*j/interior_length))`.

TRAIN fits every candidate. Combined CAL likelihood per interior symbol selects
one candidate, with listed-order tie breaking. TEST is untouched until that
selection is final.

## Frozen held summaries and pass

Compute selected-minus-K1 log gain for every TEST group. Sum by physical folio
per interior symbol, then weight folios equally. Also compute exact one-sided
folio sign probability, every leave-one-folio-out effect, maximum folio
contribution, Currier A/B views, and the same effect on exact
`(Currier, original length, interior sequence)` surfaces absent from TRAIN.

`INTERIOR_POSITION_PASS` requires a non-K1 selection; exactly 4,952 TEST groups
and 24 folios; equal-folio gain >=.015 nat/interior-symbol; >=18 positive
folios; sign p<=.01; positive minimum deletion; maximum contribution <=.15;
at least 500 unseen groups with gain >=.01 and positive minimum deletion; and
both Currier registers with gain >=.005, positive minimum deletion, and >=65%
positive folios.

The manuscript target must pass separately in manuscript and completely
reversed interior order. The selected K may differ because deterministic bins
are orientation-asymmetric at indivisible lengths. No orientation may be
selected post hoc.

## Target-free calibration

Using only masked geometry, generate 64 exact-length-conditioned iid `NULL`
worlds, eight manuscript-wide five-bin `POSITION` worlds at strength .55,
eight B-only `CURRIER_ONE`, eight `ONE_FOLIO`, and eight independently mapped
`FOLIO_RANDOM` worlds. Noise is independently keyed by TRAIN/CAL/TEST; planted
maps are shared only where the named construction requires it. Run every world
in original and reversed order.

Require at most 1/64 null passes in each orientation; at least 7/8 position
passes in each; zero passes for every adversarial family in each; identical
pass decisions under reversal for all 96 worlds; exact 24-label relabeling
invariance within 1e-10; finite scores; exact capacity; schema mutations; target
isolation; and absent target outputs. Use 32 workers with numeric threads one.

## Frozen inputs and ceiling

- masked panel SHA-256
  `0b6202641045ed11fd1ae4870353b4bec17adcc658c9687fd766f35bfbfe51ad`;
- capacity validation SHA-256
  `1513617bafcc3c4143af7be129251cf9dd7e7aa5cfa429c414c55eaa8fe923f8`;
- model core SHA-256
  `f516e87c5f0c3be14a9187ffd87f935ea92331147fd3f14241a5ad754ed7bd98`.

Only independent reconstruction of a passing synthetic preflight may authorize
one separately frozen target join. A target pass establishes interior relative-
position structure beyond endpoints and exact length. It does not establish a
prefix, root, suffix, sound, word, part of speech, language, cipher operation,
meaning, plaintext, or translation.
