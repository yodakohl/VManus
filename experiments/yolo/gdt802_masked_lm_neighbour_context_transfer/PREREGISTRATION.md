# GDT802 protocol

## Working question

GDT801 leaves 388 exact running-text events from 28 paired `Xl/Xm` surface
families.  After the target ending is hidden, does the immediately adjacent
complete EVA surface improve prediction beyond the physical line position?
Does any such gain survive outside those thirty-page events in the already
admitted V99R7 cache?

This is an architecture discriminator, not a translation test.  `stem` means
only the analyst operation “remove the final EVA `l` or `m`”.  A neighbouring
surface means one whitespace-delimited ZL3b token.  Neither is assumed to be a
morpheme, word, sound or plaintext unit.

## Populations

1. `DIRECT_388`: GDT801 exact-join running events, restricted to the 28 stems
   that retain both endings in that join.  This is the local lead.
2. `CACHE_REST_3749`: all other GDT800 paired-terminal events in the inherited
   V99R7 cache.  This is the decisive portability population.
3. `FULL_4137`: their union, reported as a sensitivity and capacity census.

No new page, image or transcription may be opened.  `f84` and `f84r` remain
forbidden.  Segmented selectors such as `f95v1/f95v2` are one physical-folio
fold (`f95v`).

## Features and models

The target surface is represented only by its hidden outcome (`l` or `m`) and,
where licensed, its derived paired-family stem.  BOS/EOS are never neighbour
features.

- `P`: six physical distance-from-line-end cells (`0,1,2,3,4,5+`).
- `S`: `P` plus a training-seen target-stem coefficient.
- `C`: `P` plus sparse, side-specific complete-left and complete-right surface
  coefficients.
- `SC`: `P` plus both stem and shared-neighbour coefficients.

The physical baseline uses a Beta(1,1) global rate and sixteen-event shrinkage
of each distance cell to that rate.  Each eligible nonbaseline coefficient is
fit as a one-dimensional ridge-logistic offset with L2 penalty 4.  Left and
right offsets are then added.  In `SC`, the stem offset is fit first and the
context offsets are fit against that training-stem-adjusted offset.  A stem needs five
training events.  A neighbour needs at least five training events and must
occur beside at least three target stems on at least three normalized physical
folios.  Eligibility is recomputed from the training fold only.  Missing,
ineligible and unseen values contribute zero.

Five folds are assigned once on `FULL_4137`, independently for stems and physical folios, by greedy
event-count balancing, with lexical tie-breaking.  Report ordinary held-folio
models and a harder 5x5 crossing: every event is scored only by the model whose
training set excludes both its complete stem fold and its complete folio fold.
The latter prevents either target-family or page echo from masquerading as
shared context.

Primary scores are event-weighted natural-log loss, Brier loss and AUC.  A
positive gain is `loss(reference)-loss(candidate)`.  A sparse shared-context
lead requires positive `C-P` crossed gain on both `CACHE_REST_3749` and
`FULL_4137`.  Installation as a portable identity channel additionally
requires the transparent alpha-20 exact-identity estimator below to retain
nonnegative loss gain and macro conditional AUC at least .5 under both
leave-one-stem and leave-one-physical-folio holdout.  This deliberately makes
estimator dependence visible.  The learned-stem claim requires positive `S-P`
held-folio gain on both populations. `SC-S` reports whether sparse context adds
after stem identity.

Two deterministic label-permutation diagnostics preserve either
physical-folio x distance cells or stem x distance cells and refit the crossed
`C` model.  They measure how exceptional the full-cache context gain is but do
not override a failed portability sign.

An independent transparent audit estimates each exact left/right identity
inside four physical position classes with fixed twenty-event shrinkage. It
reports AUC only within target-stem x position strata containing both endings.
Its outcome-blind comparison score is minus the training frequency of that
same neighbour identity and position: if rarity predicts as well as learned
identity, the result remains a lead rather than a structural role. Exact
two-sided frames receive a separate capacity census and are not pooled into a
new pseudo-word.

## Explicit special case and sensitivities

`daiin` is reported separately because it generated the clearest local
pattern.  It survives only if a left-`daiin` association adds to physical
position in `CACHE_REST_3749`; mere success of the rule “`m` at line end” does
not count.  A sensitivity masks neighbouring members of any GDT800 paired
terminal family, preventing serial `l/m` targets from becoming context
features.

## Claim ceiling

GDT802 may select physical position, learned target-family identity, sparse
shared complete-neighbour context, or a mixture as predictive architecture. It
may retire the narrow `daiin` lead. It cannot establish that `l/m` are
equivalent, suffixes, morphemes, abbreviations or inflections; cannot give
`daiin` or any neighbour a meaning; and cannot identify language, sound,
plaintext, object, ingredient, action or translation.
