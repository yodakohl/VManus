# USR001 — unparsed y-final internal-reset test

Status: **STOPPED UNSCORED — INTERNAL LAYOUT PREFLIGHT REQUIRED**.

This registration was stopped before implementation, controls, or manuscript
scoring.  The frozen `surface` field preserves physical-line order but flattens
human-marked internal continuation gaps.  Consequently an "internal" residual
position is not necessarily an ordinary within-record position.  The proposed
reset score could therefore rediscover editorially reconstructed layout breaks
rather than a new boundary system.  No statistic from the design below is
authorized.  A narrower split/fused-surface test may be registered separately.

## Disclosed discovery

The package correction was inspected before this registration. The literal
`UNPARSED_SURFACE` layer contains 3,838 groups, 2,818 of them internal. Seventeen
of 28 types end in literal `y`; they account for 3,667 events, including 2,761
internal events. The strongest neighboring surface types and the exact two-locus
`ddy` inventory are also disclosed. No line-boundary-likeness score, matched
null, or reset effect has been computed.

This test is new because all earlier formal sentence/record analyses silently
excluded these groups. It tests a complete-surface boundary relation rather
than another root, role, or semantic assignment.

## Inputs

- `results/pre_grounding_interlinear.tsv`, SHA-256
  `8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43`.
- `results/pre_grounding_surface_residual_atlas.tsv`, SHA-256
  `43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3`.
- `results/unparsed_surface_structure.json`, frozen when the implementation
  manifest is created.

Only manually transcribed literal surfaces and editorial P/A/B layout metadata
are permitted. Root sequences, roles, `word_count`, OCR, pixels, image models,
dictionaries, and proposed meanings are forbidden inputs.

## Units and target

Work separately in ZL3b, IT2a, and RF1b. A line is eligible only when its frozen
scope is `CONFIRMED_PROSE`, it has at least three literal surface groups, and a
ZL3b row exists for the same locus. ZL3b's editorial OPEN/CONT state is copied
by locus to all readings so incomplete alternate-reading paragraph markers do
not change strata.

Every internal surface position is classified as:

- `TARGET`: the position is in the residual atlas and its complete literal
  group ends in `y`;
- `CONTROL`: the position is absent from the residual atlas;
- excluded: a residual group not ending in `y`.

The primary target is the aggregate y-final residual layer, not `y`, `dy`,
`sy`, or `ddy` separately. Individual-type effects are descriptive only.

Positions are grouped by exact `(edition, page, ZL paragraph state, quartile)`.
Quartile is `min(3, floor(4*(position-1)/(line_length-1)))`. Retain a cell only
if it contains at least one TARGET and at least ten CONTROL positions. Frozen
score-blind capacity is expected to retain at least 250 ZL target positions on
100 pages, 150 IT positions on 80 pages, and 1,000 RF positions on 100 pages;
failure stops before any boundary score.

## Root-free boundary axis

For each reading separately, fit two categorical Naive-Bayes axes from all
other physical pages:

- START: first literal group of an eligible prose line versus every internal
  group;
- END: last literal group versus every internal group.

Each word contributes exactly these seven categorical features:

1. `LEN=min(character_length,8)`;
2. first character;
3. first two characters, padded with `_`;
4. last character;
5. last two characters, padded with `_`;
6. whether the surface begins `q`;
7. whether the surface ends `y`.

For every feature family, use add-one-half smoothing over the vocabulary fixed
from the entire reading, equal positive/negative class priors, and clip each
feature log-likelihood ratio to `[-4,+4]`. The page being scored contributes no
training count. Complete word identity is not a feature.

For an internal marker at position `j`, its fixed context score is:

`END_SCORE(surface[j-1]) + START_SCORE(surface[j+1])`.

The marker's own spelling never enters its score.

## Statistic and null

Within every retained cell, compare mean TARGET context score with mean CONTROL
context score. Pool cell sums within page, form one TARGET-minus-CONTROL page
contrast, then average pages equally. ZL3b is primary.

The null independently reassigns the exact target count within each retained
cell among all target/control positions. Use 8,192 deterministic uniform
without-replacement assignments derived from SHA-256 domain
`USR001|2026-08-09|assignment|cell`; random-key ties break by ascending
`(locus,position)`. The one-sided plus-one p-value counts null statistics at
least the observed statistic within `1e-12`.

For each reading, the line-boundary reference is the equal-page mean of
`END_SCORE(last group)+START_SCORE(first group)` minus the mean CONTROL context
score on the same page. The material ratio is observed effect divided by this
positive reference.

## Controls before target

Production and a nonimporting validator must agree on:

1. exact input hashes, row identity, target/control/exclusion partition, cells,
   and score-blind capacity;
2. a synthetic four-page fixture where high reset scores planted across all
   cells pass and reversed low-score labels reject;
3. exact label-count and stratum preservation for every assignment;
4. assignment zero replay, deterministic rerun, and row-order invariance;
5. genuine held line endpoints have positive reference in every reading;
6. a one-page-only synthetic plant fails the page-support and concentration
   gates;
7. no root, role, image, morphology, semantic, or target-English field is read.

No manuscript target statistic may be emitted before these controls pass and
their implementation hashes are frozen.

## Confirmation gates

All gates are mandatory:

1. capacity gates above pass;
2. every reading has a positive line-boundary reference;
3. ZL observed effect is positive;
4. ZL plus-one p is at most `.01`;
5. ZL material ratio is at least `.10`;
6. at least 60% of retained ZL pages have positive page contrasts;
7. every leave-one-ZL-page-out effect is positive;
8. no ZL page contributes more than 20% of the sum of absolute page
   contributions;
9. IT2a and RF1b effects are positive with material ratio at least `.05`;
10. deleting each literal type with at least 20 ZL target events leaves the ZL
    effect positive;
11. production controls and independent full reconstruction pass.

Failure of any gate is a nonconfirmation of this narrow internal line-like
reset mechanism. Gates may not be weakened after scoring.

## Claim ceiling

A pass would establish only that the aggregate y-final unparsed layer tends to
sit between a line-end-like left context and line-start-like right context,
consistent with an internal record reset. It would not prove punctuation,
clause boundaries, a suffix, a grammatical word, `dd+y`, a number, sound,
language, plaintext, or English meaning. A failure would reject only this fixed
surface-reset model; it would not make the residual groups meaningless.
