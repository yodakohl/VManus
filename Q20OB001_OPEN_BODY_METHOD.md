# Q20OB001 OPEN-to-BODY predictive dependence method

Status: `FROZEN_BEFORE_PAIRING_SCORE`

Date: 2026-08-14

Branch: `yolo/gdt002-visual-grammar-constraints`

## Question and scope

Does the source-native first physical line (`OPEN`) of a clean star-delimited
Q20 unit improve prediction of that unit's remaining physical lines (`BODY`)
beyond training-folio string statistics, body length/shape, and the vocabulary
of other bodies on the same held physical folio?

This is a transferable structural-dependence test. `OPEN` and `BODY` are
physical positions, not semantic labels. No recipe, header, title, field,
language, word class, meaning, plaintext, or translation is inferred.

## Frozen panel and folds

Use the 170 units in the already validated anonymous star-unit binding. Every
unit has the same 2--7-line physical span in ZL3b, IT2a, and RF1b; its first
line is OPEN and all later lines are BODY. The source-native panel is rebuilt
only from `source_sta_group_alignment.tsv`, preserving physical line and
manual source-group boundaries. It contains 510 alternate-reading rows on
eight physical folios (`f104`, `f105`, `f106`, `f107`, `f112`, `f113`,
`f114`, `f115`). The readings are sensitivities of one object, never
replications. f84r is rejected before formal fields are retained.

Run eight leave-one-physical-folio-out folds. All probability parameters and
cache weights for a held fold are learned on the other seven folios only.

## Low-capacity predictive family

Run exactly three source-native representations:

1. `MEMBER`: STA member codes, the primary endpoint;
2. `FAMILY`: STA family symbols;
3. `GROUP`: exact complete member-code source groups.

`MEMBER` and `FAMILY` use a group-reset order-2 KT model with alpha `0.5` as
the training-only string baseline. `GROUP` uses a training-vocabulary KT
dictionary plus an escape encoded by the MEMBER order-2 model. A separate
BODY-shape KT baseline encodes body line count, groups per body line, and
members per source group. It is descriptive because the conditional content
models do not encode length.

For MEMBER and FAMILY, build a unigram cache distribution from the candidate
OPEN. For GROUP, build a cache over the training group vocabulary plus escape.
EOS probability always remains the string baseline, so OPEN cannot gain by
predicting BODY length. The conditional probability is a single fixed-share
mixture of baseline and OPEN cache.

Before adding the own-OPEN cache, strengthen every held baseline with an
adversarial local-vocabulary cache built from all *other* BODY records on the
same held folio. Its weight is learned by leave-one-record-out construction on
the training folios. Thus the primary increment asks whether the particular
OPEN adds information beyond external-folio character statistics and the
held folio's unpaired following-text vocabulary.

The only fitted capacities are two sequential grid weights:

`{0, 1/128, 1/64, 1/32, 1/16, 1/8, 1/4, 1/2}`.

First choose the local-BODY weight on training folios; freeze it; then choose
the own-OPEN weight. Ties select the smaller weight. No feature, affix, root,
cluster, exception, page-specific coefficient, or deeper model is searched.

## Matched held-folio null

Within each held physical folio and reading, permute complete OPEN records only
within exact OPEN source-member-count strata. BODY, folio, body length, total
record member length, the multiset of OPENs, and all local vocabularies remain
fixed. Singleton strata remain fixed and contribute no permutation evidence.
Report the swappable-record count explicitly.

Use 4,096 SHA-seeded joint permutation worlds. The same assignment world is
used for MEMBER, FAMILY, and GROUP within a reading. The primary statistic is
held baseline bits minus conditional bits, summed across all eight folds.
Positive is better. Report inclusive plus-one local p-values and a maxT p-value
across the three registered representations. Also report the deterministic
previous-compatible-OPEN cyclic assignment within each exact-length stratum
and per-folio gains as diagnostics.

## Decision

`TRANSFERABLE_OPEN_BODY_DEPENDENCE_SUPPORTED` requires all of:

- positive primary MEMBER gain in ZL3b;
- MEMBER maxT `p<=0.05`;
- positive MEMBER gain in IT2a and RF1b;
- positive MEMBER gain on at least six of eight ZL3b held folios;
- true MEMBER pairing beats the deterministic previous-OPEN assignment; and
- the selected own-OPEN weight is nonzero in at least six ZL3b folds.

`OPEN_BODY_DEPENDENCE_WEAK_OR_FOLIO_LOCAL` applies to a positive nominal lead
that misses any transfer or multiplicity gate.

`OPEN_BODY_DEPENDENCE_NOT_ABOVE_MATCHED_CONTROLS` applies when the primary
gain is nonpositive or the true pairing is not better than its matched-null
median.

`INSUFFICIENT_OPEN_BODY_CAPACITY` applies if fewer than 100 records are
swappable in any reading or fewer than seven physical folios survive.

## Claim ceiling

Even a positive result establishes only transferable source-internal
dependence between a star-unit's first line and its later lines. It cannot
establish a recipe, heading, title, argument structure, semantic field,
language, word, morpheme, POS, plaintext, meaning, or translation.
