# LTG001 — latent transcription-channel reconstruction

Status before execution: **CAPACITY AND MODEL FROZEN; HELD-FOLIO SCORES UNOPENED**.

## Nonduplicate question

The three source-native manual readings (ZL3b, IT2a, RF1b) agree at most fine
STA positions, but retain recurrent disagreements.  LTG001 asks whether those
three observed member-code streams can be explained by a small, reusable
latent suffix-state inventory and three stable edition-specific observation
channels that transfer to whole held physical folios.

This is not the stopped member-resolution test.  That experiment asked whether
exact member codes added endpoint-role information beyond coarse family
shells.  LTG001 instead predicts one manual reading from the other two at the
same physical position.  It does not select an endpoint, a glyph opposition,
or a preferred transcription.  It is also not RTA001: no diagram relation or
text-to-text edit operator is used.

## Frozen source and panel

Input is the validated strict, zero-alternative part of
`source_sta_family_consensus_groups.tsv`.  Every aligned position contributes:

* physical folio, page, Currier state, and within-group position;
* one common coarse STA family;
* the three source-native fine member suffixes, with the family letter removed.

The panel retains all aligned positions.  The primary diagnostic subset has
the two predictor editions disagreeing, so predicting the third edition
cannot be solved by an unexamined majority rule.  ZL3b, IT2a, and RF1b are
alternate readings of one manuscript, not replications.

Physical folios are assigned to five deterministic folds by the first four
bytes of `SHA256("LTG001_FOLD_V1|" + physical_folio)`, interpreted big-endian,
modulo five.  No position from a held folio enters its training fit.

## Capacity gates

Before model fitting, require all of:

1. at least 3,000 disagreement positions on at least 80 folios;
2. at least 5,000 ambiguous target-edition prediction events on 80 folios;
3. at least 50 exact disagreement triplets recurring on three folios;
4. at least 5,000 ambiguous events whose exact ordered predictor context has
   at least five occurrences outside the held folio;
5. every deterministic fold contains at least 500 disagreement positions;
6. after removing the single dominant `(B1,B1,Ba)` policy, at least 1,500
   disagreements on 60 folios remain;
7. both Currier A and B contain at least 500 disagreements; and
8. at least five families contain 20 disagreements on ten folios.

Failure stops LTG001 before model fitting.

## Models

All probabilities use train-only counts and a frozen symmetric Dirichlet
pseudocount of 0.25.

`DIRECT` is the strongest admissible baseline.  For target edition `e`, it
estimates the exact conditional distribution
`P(o_e | family, o_a, o_b)` from training folios, backing off to
`P(o_e | family)` when the ordered predictor context is unseen.

`CHANNEL_K` is a latent categorical model.  The hidden suffix state `h` is
shared across families.  Each family has a train-only prior `P(h | family)`;
each edition has one reusable emission matrix `P(o_e | h)`.  The observed
triple likelihood is

```text
sum_h P(h | family) P(o_ZL | h) P(o_IT | h) P(o_RF | h).
```

Candidate sizes are `K = 2, 3, 4, 6, 8`.  For each outer held-folio fold, K is
selected only by minimum BIC on its training positions.  EM starts from eight
deterministic seeds, stops at relative likelihood change below `1e-10` or 500
iterations, and retains the maximum-likelihood restart with a byte-order
tie-break.  Hidden states remain anonymous `H01`, `H02`, ... .

## Synthetic calibration

Before manuscript scoring, the implementation must pass fixed synthetic
worlds with the same family and folio geometry:

* 16 `NULL_DIRECT` worlds generated directly from conditional lookup tables;
* 16 `SHARED_CHANNEL` worlds with 2--6 planted reusable hidden states;
* 8 `ONE_FOLIO_CHANNEL` worlds;
* 8 `FAMILY_PRIVATE_CHANNEL` worlds;
* 8 `DOMINANT_POLICY_ONLY` worlds.

The instrument must yield no more than one positive decision in each negative
family, recover at least 14/16 shared-channel worlds, and select the planted K
within one state in at least 12/16 shared-channel worlds.  Synthetic labels are
generated without manuscript member identities.

## Primary statistic and essential robustness

The one primary statistic is the equal-physical-folio held-out proper-score
gain, in bits per ambiguous event, of selected `CHANNEL_K` over `DIRECT`.
Folio gains are computed by averaging event log2 gains within each folio and
then averaging folios equally.  The exact sign-test p-value is the inclusive
upper Binomial(n, 0.5) tail for the number of positive folios.

Confirmation requires:

* gain at least +0.020 bit per ambiguous event;
* exact folio sign p <= 0.01;
* positive gain in both Currier A and Currier B, each at least +0.010;
* positive gain after deleting every `(B1,B1,Ba)` position;
* positive gain on exact predictor contexts unseen in training; and
* every leave-one-folio deletion of the equal-folio aggregate remains positive.

These are robustness conditions on one claim, not separate discoveries.

## Interpretation ceiling

A pass may establish only that a small anonymous latent suffix-state system and
stable edition-specific observation channels predict held-folio manual-reading
variation better than direct train-only triplet lookup.  It cannot select the
physically correct reading or establish authorial glyph identity, allography,
sound, alphabet, cipher values, wordhood, morphology, language, plaintext,
meaning, or translation.

A failure closes the reusable three-reading channel at this STA resolution.
It would imply that the next transcription route needs direct image-grounded
grapheme reconstruction rather than another relabeling of the current codes.
