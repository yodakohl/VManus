# CMR001 — drawn circle-marker reset test

Status: **REGISTERED_UNSCORED**

## Question and non-duplication

Do human-catalogued drawn strokes/squares at circular-text cuts select a group
that resembles an ordinary physical-line initial group more than other cyclic
positions in the same ring?

This is not CC001--CC003: those tested cyclic separators, rates, and whole-ring
grammar without authorial phase. It is not the stopped universal zodiac-degree
route. The new independent variable is a public human-described drawn mark at
an exact ring seam. The response is a line-initial likeness model learned only
from non-circle prose outside f67--f73.

## Frozen inputs and isolation

- `results/circle_marker_reset_capacity.json` and its validation define the
  exact 22-marker, 18-conservative-marker, and 25-no-obvious-start locus sets.
- `results/source_sta_group_alignment.tsv` supplies complete manual STA family
  sequences in source-group order.
- `results/source_separator_transcription.tsv` supplies page, physical folio,
  kind, scope, and source-group identity.
- ZL3b, IT2a, and RF1b are alternate readings, never independent samples.
- Training excludes every row on physical folios f67--f73. Target/control
  locus membership is not available to the training function.
- No retained parser root, role, formal interlinear, OCR, image feature, modern
  vision output, English gloss, label string, or illustrated-object attribute
  may enter the model.

## Frozen line-initial likeness model

Fit one categorical naive-Bayes model per reading on `CONFIRMED_PROSE`, IVTFF
kind `P`, outside f67--f73. A training group is positive exactly when its
source-group index is 1 and negative otherwise. The model uses equal class
priors.

For STA family string `w`, use exactly seven categorical fields:

1. `LEN`: `min(len(w), 12)`;
2. prefixes `P1`, `P2`, `P3`, using the whole string when shorter;
3. suffixes `S1`, `S2`, `S3`, using the whole string when shorter.

For each field independently, use add-one smoothing over the training
vocabulary plus an explicit unseen category. The score is the sum of the seven
positive-minus-negative log conditional probabilities. Do not use an exact
whole-string field, feature selection, learned embedding, or tuned penalty.

Target-blind calibration is leave-one-physical-folio-out within the eligible
training corpus. Tied AUC uses half credit. Calibration passes only if every
reading has equal-folio mean AUC >= .65, median folio AUC >= .65, and at least
75% of eligible folios have AUC >= .55. Failure stops before target scoring.

## Frozen within-ring score

For each reading and locus, score all source groups. For candidate position
`j`, define centered percentile

`r = (number(score < score_j) + .5*number(score == score_j))/n - .5`.

The observed position is source-group index 1, already bound to the public
marker/cut before model construction. Average `r` first across loci within a
physical folio, then equally across physical folios. This gives one `T_e` per
reading. The primary statistic is `M = min_e(T_e)`.

The primary panel is all 22 markers. The 18-locus conservative panel is a
mandatory sensitivity. The 25 disjoint no-obvious-start loci are a mandatory
negative control, not an alternative discovery target.

## Frozen phase null

Use 65,536 deterministic assignments. For assignment `a` and physical locus
`l`, obtain an unsigned 64-bit integer from the first eight bytes of
`SHA256("CMR001_PHASE_V1|a|l")`, divide by `2**64` to get `u`, and choose
`(observed_index_e + floor(u*n_e)) mod n_e` in each reading-specific sequence.
Thus all readings receive the same normalized physical phase while retaining
their own manual spacing, and a simultaneous cyclic reindexing is exact.
Assignment zero is not special. Compare with tolerance `1e-15`; use plus-one
upper-tail p `(1 + #null >= observed)/(65536 + 1)`.

The scorer must emit exact score-array, percentile-array, assignment-index,
null-orbit, folio-effect, and result digests. Positive affine score transforms,
simultaneous cyclic rotation, row serialization, and reading-order changes
must leave ranks/statistics invariant after canonical reordering.

## Frozen controls and gates

Before opening target score arrays, synthetic rank-array controls must:

- recover a distributed six-folio/all-reading marker plant;
- reject a null plant, one-folio plant, and one-reading-disagreement plant;
- reject a synthetic no-obvious-start panel under the same primary gates;
- preserve cyclic-rotation, positive-affine, serialization, and reading-order
  invariance;
- prove the 65,536-assignment generator and synchronized-reading index maps
  deterministic by fixed digests.

The manuscript result confirms only if all gates pass:

1. target-blind line-initial calibration passes in all readings;
2. all-marker `M >= .10` and null p <= .05;
3. conservative-marker `M >= .08` and null p <= .05;
4. each reading's all-marker `T_e > 0`;
5. each reading is positive on at least 5/6 physical folios;
6. every leave-one-folio-out all-marker `M > .05`;
7. no folio contributes more than .35 of total absolute all-marker folio
   effect in any reading;
8. the no-obvious-start panel does not satisfy both `M >= .10` and p <= .05;
9. all-marker `M - no-obvious M >= .05`;
10. all controls, hashes, target isolation, finiteness, and independent
    reconstruction pass.

No gate, feature, locus class, uncertainty rule, or threshold may change after
any target score is opened.

## Claim ceiling

On pass: public drawn circle markers preferentially select locally
line-initial-like groups, supporting a local record/reset seam at this aggregate
panel. This would license separately preregistered marker-local phase tests.

On failure: this fixed STA-family line-initial representation does not support
the reset hypothesis; the marks remain physical layout features.

Neither outcome establishes clockwise direction, a universal top-left start,
inter-band continuation, zodiac degree order, wordhood, punctuation, a number,
sound, language, English meaning, plaintext, or translation.
