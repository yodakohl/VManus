# Unordered per-sign ruler-tuple model: novelty audit

Date: 2026-09-15. This is a source and contract audit only. No new target
labels, images, reserves, or target tests were opened.

## Proposed finite model

For each known sign `s`, define the external 30-record table

`T(s,d) = (D(s,d), E(s,d), M(s,d)[, H(s)])`, for `d = 1..30`,

where `D` is the decan ruler, `E` the Egyptian-term ruler, `M` the
degree-ruler/monomoirion, and optional `H` is the sign's domicile ruler. The
Voynich figure labels belonging to sign `s` are treated as one unordered bag of
30 complete labels. Their assignment to the 30 records is an independently
free permutation `pi_s`; no origin, direction, band continuation, or shared
phase is fitted.

The proposed content mechanism is one common planet code `C(p)` reused in all
roles and signs, with the role order fixed as `D,E,M[,H]`. This gives a finite
model only after freezing the seven-planet inventory, the delimiter or
concatenation convention, and the historical table variant. The anonymous
code-name permutation is at most `7!`; `H` is two predeclared model variants,
not a choice made after seeing labels. The `pi_s` permutations are nuisance
assignments within signs, not evidence for an origin or a visual order.

Before any target exposure, the source side can enumerate, for every frozen
table variant:

* the multiplicity spectrum of equal tuples within each sign;
* cross-sign equality classes and the role-by-role equality matrix;
* the component co-occurrence spectrum implied by the shared `C`; and
* collisions introduced by un-delimited concatenation.

Those are concrete predictions of a shared code. A later target census would
compare the same spectra under all `pi_s` to an independent-per-sign code null,
preserving complete-label boundaries and all three manuscript readings. A
nontrivial shared co-occurrence pattern that survives the per-sign permutation
null would justify a finite decoder-selection pass. A spectrum with no
repeated constraints, or a result requiring arbitrary code strings or
sign-specific repairs, would close this candidate before semantic wording is
attempted. Neither outcome is being claimed here.

## What was already tested

GDT337 is the nearest external-source predecessor. Its A-65 comparator records
12 signs, 30 degrees per sign, three ten-degree parts, seven luminaries and a
1--28 lunar schedule. Its gates required a readable external order and
ownership, a text-blind target correspondence, and a disjoint physical-folio
holdout. It found no viable frozen endpoint. The proposed bag model removes
the exact requirements that failed there: it does not transfer external slot
order, choose a target origin, or claim a visual one-to-one diagram. It is
therefore a different formal question, but GDT337 still blocks any claim that
the source table grounds a Voynich sign or label.

The cross-sign phase-capacity audit found 299 labels in 300 public positions,
seven incompatible panel topologies, and no disjoint-folio repeated topology.
Its stop rule was specifically against fitting a common degree phase, band
order, or continuation. The unordered model does not use those coordinates,
so that stop does not directly falsify it. Conversely, the model gives up the
main protection supplied by that stop: independent `pi_s` assignments can
absorb almost any within-sign arrangement.

GDT794 tested 199 complete circle-label strings and found only 15 repeated
strings, with eight recurring across physical folios. GDT795 then tested
source-native family sequences for 101 Kluge-A labels, including one shared
rotation/reflection per whole diagram and held A-member retrieval. It found no
reusable position code; the retained architecture was learned member names
plus a local graphical/register field. Those experiments did not test a
complete 30-label-per-sign unordered multiset against fixed ruler tuples, so
they are close controls rather than duplicates. Their low recurrence is a
material feasibility warning: the new mechanism needs component-level
co-occurrence, not merely exact whole-label repetition.

The duplicated-sign cross-role and opposition-profile routes scored source-
native n-gram/profile similarity under 1,485 and 105 fixed sign matchings,
respectively. The Taurus-repeat audit discarded direction and still found no
consistent homologous local context. None enumerated externally fixed
decan/term/degree tuples with free within-sign assignment. The new model is
distinct from these matching contracts, while it must not reuse their
post-result pair or profile mining as evidence.

GDT398 is the closest tuple-compiler warning: free latent compression of 1,676
opaque joint tuples was explained by frequent existing structure and failed
stability/held-fold gates. The present proposal can differ only if the ruler
tables are frozen before target access and the shared code is tested against a
predeclared independent-sign null. An unconstrained codebook would simply
repeat GDT398's underdetermination under astrological names.

## Source and novelty limits

The original report named by the closed family row,
`semantic_assumptions/results/oresme_source_family_feature_test_v2_report.md`,
is absent from the repository. The family row says that element, season,
polarity, planet, fate, Oresme, and serialized visual-order mappings failed
held controls, but the family review explicitly records `primary_sources_read:
[]` and retains this as an inherited summary. It cannot be treated as an
independently checked refutation of the present unordered model. GDT337's
source audit is the available primary comparator and does not supply a
Voynich correspondence.

The strongest novelty claim is thus narrow: a source-fixed, order-free
per-sign multiset of ruler tuples with one shared planet-code mechanism has not
been the contract of the cited predecessors. It is not yet a meaning model or
a decoded word model.

## Required freeze before any target test

Freeze the exact historical ruler tables and term-boundary convention; run the
`H`-included and `H`-omitted variants separately; specify code boundaries and
collision handling; retain every complete label and edition; and define the
independent-per-sign permutation null before target access. Do not infer that
identical strings denote identical objects, or that every figure label names a
degree record.

The decision consequence is finite: a shared role-conditioned equality and
co-occurrence signal would make this the next zodiac test; absent such a
signal, or with gains obtained only by arbitrary `C`/`pi_s` repairs, the route
should leave the zodiac ruler family rather than reopen phase/order fitting.
