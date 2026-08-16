# GDT163 — substitution context-transfer report

Decision: **PRODUCTIVE_INTERNAL_SUBSTITUTION_TRANSFER_INTERESTING**.

## HPR2 outer-context transfer

The frozen short-host inventory yields 660 section×hand cells from
153 directed substitution classes; 65 classes meet the four-cell transfer threshold.

| split | model | predictions | fractional MSE gain | mean cosine | positive-dot rate |
| --- | --- | ---: | ---: | ---: | ---: |
| `HELD_BASE` | `OP_SUBSTITUTION` | 322 | +0.113470 | +0.493394 | 0.889 |
| `HELD_BASE` | `POSITION_ONLY` | 660 | -0.008405 | +0.144482 | 0.648 |
| `HELD_BASE` | `EXACT_PAIR_OTHER_STRATA` | 493 | +0.666642 | +0.683748 | 0.937 |
| `HELD_BASE_AND_SECTION` | `OP_SUBSTITUTION` | 261 | +0.098672 | +0.471058 | 0.876 |
| `HELD_BASE_AND_SECTION` | `POSITION_ONLY` | 660 | -0.013306 | +0.141354 | 0.646 |
| `HELD_BASE_AND_SECTION` | `EXACT_PAIR_OTHER_STRATA` | 491 | +0.653483 | +0.673154 | 0.934 |
| `HELD_BASE_AND_HAND` | `OP_SUBSTITUTION` | 252 | +0.076847 | +0.461021 | 0.872 |
| `HELD_BASE_AND_HAND` | `POSITION_ONLY` | 660 | -0.009810 | +0.142813 | 0.641 |
| `HELD_BASE_AND_HAND` | `EXACT_PAIR_OTHER_STRATA` | 485 | +0.654273 | +0.672803 | 0.928 |


The primary operation learner's position-preserving aggregate p is
0.033171; its best-operation maxT p is
0.000976.  Exact-pair transfer is shown only
as a separate baseline and never enters the learned substitution vector.  The
predictive hierarchy is exact host-pair identity
(+0.666642)
above substitution class (+0.113470) above
position alone (-0.008405).  The
substitution signal is therefore transferable but does not replace lexical
identity.

## Strongest specific substitutions

| operation | cells/bases | sections/hands | held-base gain | held-section | held-hand | cosine | maxT p | dominant observed/predicted deltas | label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `L3:P3:a>y` | 8/6 | 3/3 | +0.9135 | +0.8681 | +0.8694 | +0.9613 | 0.0010 | `b3=0:+0.8558/+0.8246|b3=1:-0.8558/-0.8246|right_family=NONE:+0.1352/+0.1198|local_frame=NONE:+0.0758/+0.0711` | `INTERESTING_EXPLORATORY` |
| `L3:P3:e>y` | 17/7 | 4/4 | +0.8251 | +0.8145 | +0.8112 | +0.9143 | 0.0010 | `dy_closure=0:+0.8430/+0.8109|dy_closure=1:-0.8430/-0.8109|wrapper=q:-0.0780/-0.0306|local_frame=OT:+0.0565/+0.0903` | `INTERESTING_EXPLORATORY` |
| `L3:P1:l>o` | 5/3 | 2/2 | +0.8093 | +0.0000 | +0.0000 | +0.9119 | 0.0010 | `wrapper=q:+0.5886/+0.5784|wrapper=NONE:-0.4954/-0.4973|right_family=NONE:+0.1434/+0.1186|local_frame=NONE:+0.0891/+0.0812` | `WEAK` |
| `L2:P2:s>t` | 10/4 | 5/4 | +0.6395 | +0.5289 | +0.5424 | +0.8370 | 0.0049 | `right_family=NONE:-0.5707/-0.4551|wrapper=NONE:+0.3611/+0.2290|right_family=aiin:+0.2358/+0.1807|wrapper=che:-0.1602/-0.1791` | `INTERESTING_EXPLORATORY` |
| `L3:P1:e>l` | 10/4 | 4/4 | +0.6343 | +0.5766 | +0.5673 | +0.8221 | 0.0049 | `wrapper=NONE:+0.4992/+0.4799|wrapper=sh:-0.4313/-0.3972|local_frame=OT:-0.1060/-0.1073|local_frame=NONE:+0.0944/+0.0991` | `INTERESTING_EXPLORATORY` |
| `L3:P3:d>o` | 4/3 | 2/3 | +0.6158 | +0.0000 | +0.0000 | +0.8065 | 0.0059 | `right_family=NONE:+0.4452/+0.4208|dy_closure=0:-0.3594/-0.3890|dy_closure=1:+0.3594/+0.3890|right_family=ar:-0.2024/-0.1982` | `WEAK` |
| `L3:P3:d>y` | 9/5 | 4/3 | +0.5883 | +0.5718 | +0.5656 | +0.7778 | 0.0078 | `right_family=NONE:+0.5512/+0.5360|right_family=ar:-0.2006/-0.1941|right_family=aiin:-0.1748/-0.1718|wrapper=sh:+0.1010/+0.0854` | `INTERESTING_EXPLORATORY` |
| `L2:P2:k>r` | 13/3 | 6/5 | +0.5872 | +0.6349 | +0.7108 | +0.7790 | 0.0078 | `right_family=NONE:+0.7752/+0.6278|wrapper=q:-0.3632/-0.0095|right_family=aiin:-0.2956/-0.2804|right_family=ar:-0.1821/-0.0923` | `INTERESTING_EXPLORATORY` |
| `L3:P1:l>p` | 5/3 | 2/2 | +0.5389 | +0.0000 | +0.0000 | +0.7780 | 0.0166 | `right_family=NONE:-0.3789/-0.3567|right_family=aiin:+0.2114/+0.1918|wrapper=NONE:-0.1229/-0.1568|right_family=ar:+0.0620/+0.0732` | `WEAK` |
| `L3:P3:k>y` | 6/3 | 4/2 | +0.5244 | +0.0000 | +0.0000 | +0.7396 | 0.0166 | `right_family=NONE:+0.6618/+0.7542|wrapper=NONE:-0.2875/-0.1776|right_family=ain:-0.2285/-0.3287|right_family=aiin:-0.1713/-0.2042` | `WEAK` |
| `L3:P3:k>o` | 4/3 | 3/2 | +0.4605 | +0.0000 | +0.0000 | +0.6975 | 0.0351 | `right_family=NONE:+0.4190/+0.4242|dy_closure=0:-0.3383/-0.2438|dy_closure=1:+0.3383/+0.2438|right_family=ain:-0.2155/-0.2708` | `WEAK` |
| `L3:P2:k>r` | 5/3 | 4/3 | +0.4299 | +0.3198 | +0.5463 | +0.6779 | 0.0390 | `wrapper=q:-0.2711/-0.3195|right_family=NONE:-0.2481/-0.2135|local_frame=NONE:-0.1557/-0.1144|dy_closure=0:-0.1471/-0.0624` | `INTERESTING_EXPLORATORY` |


These rows are selected after scoring and receive maxT rather than local-only
labels.  Character names are frozen HPR2 display characters, not inferred
manuscript graphemes or sounds.

## Identical generic local-sequence control

| corpus | capacity | cases/predictions | op gain | position gain | increment | cosine | positive-dot | null p | top maxT p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `IFORAL_1395_1411_GRAPHEMATIC` | `POWERED` | 602/113 | -0.35511 | -0.02722 | -0.32789 | +0.0755 | 0.599 | 0.3122 | 0.3844 |
| `LATIN_15C_GRAPHEMATIC` | `POWERED` | 1121/294 | -0.30893 | -0.00513 | -0.30380 | +0.0097 | 0.471 | 0.1083 | 0.4390 |
| `LATIN_GERMAN_APOTHECARY_LATE15` | `LOW_CAPACITY` | 66/0 | +0.00000 | +0.03270 | -0.03270 | +0.0000 | 0.000 | 0.9990 | 0.9990 |
| `LATIN_MEDICAL_GRAPHEMATIC` | `POWERED` | 1381/348 | -0.34181 | -0.01614 | -0.32566 | +0.0419 | 0.515 | 0.1424 | 0.1834 |
| `LATIN_SCHOLASTIC_GRAPHEMATIC` | `POWERED` | 1707/431 | -0.29999 | -0.00993 | -0.29005 | +0.0537 | 0.549 | 0.0556 | 0.2976 |
| `VOYNICH_PAGE_HOST` | `POWERED` | 500/232 | -0.06447 | -0.04054 | -0.02393 | +0.2601 | 0.743 | 0.0351 | 0.0595 |


This endpoint is deliberately modest: previous/next contiguous form length and
within-unit position.  It is the only context representation applied
identically to Voynich and the historical corpora.  GDT159 sampled gaps remain
`MISSING`; they are not reinterpreted as record boundaries.  Voynich's absolute
gain on this common endpoint is -0.064470,
so it is negative even though it is less negative than every powered historical
control.  This is relative specificity, not successful generic sequence
prediction.

## Interpretation

The result tests whether a repeated surface substitution carries a portable
formal-context delta beyond exact host identity and position.  Even a positive
result is not a linguistic morphology finding: GDT003's string ceiling and
GDT162's exact-identity advantage remain in force.  The strongest specific
effects mostly change frozen HPR2 closure/renderer dimensions, especially B3
for `L3:P3:a>y` and DY for `L3:P3:e>y`.  PAGE_HOST and those dimensions are
parsed from the same source group, so frozen orthotactic/compiler coupling is a
live alternative to a productive internal operator.  This experiment supports
an exploratory predictive surface relation only.  No substitution receives a
function, morpheme, phoneme, language, semantic role, meaning, plaintext, or
translation.

All f84 rows were rejected before retention.  The actual source has zero f84r
rows; f84r was not opened, queried, retained, joined, or scored.
