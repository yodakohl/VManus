# GDT311 — held-folio operation event-choice test

## Question

GDT303 established three sparse operations on compatible exact surface pairs,
while GDT310 found that source-side ecology cannot predict which hosts license
them.  GDT311 asks the remaining generative question: once an exact pair is
known to be licensed, can external context predict whether an occurrence uses
the source or target surface on a completely unseen physical folio?

This differs from GDT036's `ch/che/sh` multiway wrapper analysis and from
GDT286/GDT289's all-wrapper host models.  It scores only the three frozen
GDT303 operations and requires incremental held-folio codelength beyond an
exact-pair prior.  It remains post-selection because GDT303 selected the
operations on this manuscript.

## Frozen panel and split

- operations: `ch->s`, `d->s`, and `NONE->q`;
- exact source/target surface pairs: the published GDT303 rows only;
- no other surface may enter;
- deterministic test folio if
  `sha256("GDT311_SPLIT_V1|" + physical_folio) mod 3 == 0`;
- training is every other physical folio;
- retain a pair only when both surface roles occur in training.

All 53 exact pairs pass: 7 `ch->s`, 8 `d->s`, and 38 `NONE->q`.  The test
panel contains respectively 150, 262, and 694 events.  No f84 row is eligible.

## Frozen models

All models contain a ridge-shrunk exact-pair intercept and are fit on training
folios only by ridge-10 logistic regression.

1. `PAIR`: exact-pair rate only.
2. `PAIR_POSITION`: add physical line first/last/relative position,
   DY-derived field first/last, and record-1.
3. `PAIR_BOUNDARY`: add preceding physical group's DY closure and line start.
4. `PAIR_REGISTER`: add section, Currier, hand, and composite register.
5. `PAIR_FULL`: add every declared external feature.

The same group's wrapper, frame, inner-D, right family, DY, B3, host glyphs,
host substrings, and target surface identity beyond its anonymous pair ID are
forbidden predictors.  `PREV_DY` is read only from the immediately preceding
physical group.

Score held binary log loss, Brier score, AUC, and AP.  The primary increment
is `PAIR - PAIR_FULL` in held log2 loss per event.

## Exact held-out null

Predictions are frozen from training folios.  In 8,192 worlds, permute held
source/target outcomes inside exact `pair × register` strata.  This preserves
pair availability, target frequency, and register mixture and destroys only
within-register alignment with position/boundary features.  Report local and
max-12 tails across three operations and four increments.  A pair-only
permutation is a declared confound sensitivity, not a second decision test.

Call an operation `HELD_EVENT_CHOICE_TRANSFER` only when FULL held bits/event
gain is positive, null-centered gain is positive, AUC is at least .60, and
max-12 p is at most .05.

## Claim ceiling

At most this supports a stochastic formal operation-choice rule on already
licensed exact pairs.  It cannot discover unseen licenses or identify a
morpheme, grammatical category, meaning, sound, language, plaintext, or
translation.  No f84 row may be opened, parsed, retained, joined, or scored.
