# GDT374 — common functional-operator discovery

Status at publication: **FROZEN_NOT_RUN**.

## Question

Do record-level rewrites over opaque atomic GDT327 tuples behave as reusable
operators across unrelated base fields/records and unseen physical folios, or
are they explained by tuple frequency, placement, record length, and local
template recurrence?

This is one common discovery instrument for the GDT373 registry.  It does not
test guessed meanings separately.

## Input firewall

Primary input is `gdt327_joint_tuple_interlinear.tsv`.  Joint tuples remain
atomic; `host_id`, PAGE_HOST, coordinate decomposition, observed surface, and
glyph/string similarity are forbidden predictors.  The drawing-reset atlas is
read through `GuardedTSV`: raw `page` is checked first, every `f84*` row is
discarded before the rest of the row is parsed, and only GDT327 loci are
retained.  No global source table may be parsed and filtered afterward.

ZL3b/IT2a/RF1b are alternate observations, never sample multiplication.  The
GDT327 atomic identity view is primary; reading robustness is reported as
unassessed where an exact atomic ID lacks an edition-independent analogue.

## Record units

The instrument constructs three nested scopes:

1. `FIELD`: consecutive atomic tuples with one GDT327 field ordinal.
2. `DRAWING_RESET_SEGMENT`: consecutive GDT327 tuples sharing a source-native
   drawing-reset segment ID.
3. `PHYSICAL_LINE`: the complete source-native locus.

Each record retains only opaque tuple IDs plus physical folio, page, section,
register, Currier, hand, record/field ordinal, DY/B3 closure, line/reset
boundaries, group count, and consensus left/right separator profiles.

## Frozen rewrite library

Pairs are found by exact sequence indexing, never approximate glyph distance.
The complete permitted library is:

- one atomic tuple inserted/deleted at prefix, suffix, or internal position;
- one atomic tuple replaced at prefix, suffix, or internal position, with at
  least one unchanged atomic anchor (`length >= 2`);
- two separated tuple replacements with at least one unchanged anchor;
- adjacent exact-tuple duplication;
- identical tuple sequence with one field or drawing boundary split/join;
- a current record obtainable from the immediately previous record by one or
  two tuple deletions (`SHORTEN_RESUME`).

No substring transformation, tuple merge, PAGE_HOST factorization, or
coordinate-state delta is admitted.  Rules with zero or inadequate capacity
remain explicit zeros rather than triggering library widening.

## Primary predictive task

The powered primary is `FIELD_ONE_TUPLE_INSERTION`.

Within each physical folio, exact short and long field sequences define a
rewrite event when the long sequence equals the short sequence plus one atomic
tuple.  The target class is `(PREFIX|SUFFIX|INTERNAL, inserted_tuple_id)`.
Source-side features are:

- source field length and field-ordinal bucket;
- section/register/Currier/hand and line/record entry state;
- unordered atomic source-tuple identity features;
- first and last atomic source-tuple identities.

The baseline receives all layout/position/length features but no atomic source
identities.  The full model is a training-only additive-smoothed multinomial
naive-Bayes classifier.  Exact class labels, vocabulary, smoothing counts, and
normalization are learned inside each held-physical-folio fold.  Events whose
target class is unseen in training contribute to coverage but not conditional
log loss.

Report held codelength gain, bits/event, top-1/top-5, coverage, folio-balanced
signs, held-section/register/hand sensitivities, and per-operator gain.  A
candidate is ranked by held contribution, distinct opaque base sequences,
physical folios, and registers—not raw count.

## Secondary descriptive tasks

Replacement, paired replacement, split/join, duplication, line/segment
insertion, and prior-record shortening use the same registry and capacity
schema.  They are descriptive unless they independently meet the frozen
promotion thresholds.  No post-hoc endpoint becomes primary.

## Null and search accounting

The primary coupling-destruction null permutes target operator classes among
rewrite events within the finest mobile cells of:

`scope × rewrite-position × section × register × Currier × hand × source-length × field-ordinal-bucket × line-entry`.

This preserves the complete event panel, target-class frequencies within each
cell, source tuple identities/recurrence, record length, position, layout, and
operator support, while destroying only source-record/operator pairing.  The
same permutation is used across all candidate scores in a world.  Use 4,096
deterministic worlds and report local and max-library tails.  If fewer than 50
target-mobile events remain, the null is labelled capacity-limited rather than
exact confirmation evidence.

Selector cost is `log2(number of distinct target operator classes retained by
the training fold)` for the primary family.  Candidate-specific paid gains also
charge `log2(number of globally enumerated candidates in that rewrite family)`.

## Candidate promotion

Discovery retains every capacity-eligible candidate and labels it
`INTERESTING_EXPLORATORY`, `WEAK`, `LIKELY_REGISTER_OR_LAYOUT_CONFOUND`,
`UNSTABLE`, or `NO_SIGNAL`.  Prospective promotion requires:

- at least three distinct base sequences and two physical folios;
- positive selector-paid held gain;
- positive aggregate gain after every powered leave-register sensitivity, or
  an explicitly frozen register-specific claim;
- max-library `p <= 0.05` under a null with at least 50 mobile events;
- no reduction to a known renderer, exact-record cache, or tuple-frequency
  baseline;
- a non-f84 prospective panel frozen before its tuple identities are exposed.

## Claim ceiling

Anonymous record-conditioned formal rewrite behavior only.  No coordinator,
negation, relation, anaphor, word, morpheme, POS, sound, language, plaintext,
meaning, or translation is established.
