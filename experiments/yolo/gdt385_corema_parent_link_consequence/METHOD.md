# GDT385 — external parent-link relational consequence

## Question

Can a comparator role recovered from an opaque, composite, Voynich-like
observation improve prediction of a genuinely external editor relation: whether
the pivot points backward to an earlier instruction and which earlier element
is selected?

This is comparator-only instrument calibration.  It does not reinterpret
GDT384, and it has no Voynich stage unless every frozen comparator requirement
passes.

## Strict source/outcome separation

`X` contains only GDT382 information available at or before the pivot:

* opaque host-like identity;
* rendered group;
* wrapper, position, boundary, record and renderer construction;
* composite joint state;
* the preceding two-element construction span;
* frequency, recurrence, field/record position, previous host and record
  length as candidate grammar evidence.

`Y` is built only from the hidden CoReMA `parent_instruction_ordinal`.  Its
classes are `NONE` or exact backward physical-element distances `D1..D13`.
The hidden `INSTRUCTION` role is consulted only to map the editor ordinal to
the correct earlier element.  Hidden words, concepts, English labels, roles,
POS and meanings never enter `X`.

The scorer rejects any predictor column containing `semantic`, `oracle`,
`concept`, `role`, `parent`, `english`, `label` or `instruction`.  It also
asserts that all positive targets are strictly earlier and observable.

## Frozen roles and folds

The jointly charged family is fixed in `gdt385_role_manifest.tsv`:

1. `CMP_PARENT_01` (`REF` in the hidden oracle);
2. `CMP_PARENT_02` (`TIME`);
3. `CMP_PARENT_03` (`ALTERNATIVE`);
4. `CMP_PARENT_04` (editor exclusion annotation).

Readable names are comparator evaluation labels only and never transfer to a
target.  The six CoReMA collections are six whole-collection folds.  Opaque
realization counts, role labels, parent links and outcome distributions are
learned without the held collection.

## Role recovery

The frozen GDT383 domain-local hierarchy is reused without retuning: five
resolution-specific Laplace naive-Bayes scores are combined by median log odds
and combined with the seven grammar channels.  The exact-joint and constant
models are retained as baselines.  No result from GDT384 selects a realization.

## Relational predictor

The source baseline predicts the 14-way relation outcome from a fixed
source-side stratum:

`position × boundary × field index × within-field index × record-length bin ×
 recurrence bin × global opaque-frequency bin`.

For each held collection, a hierarchical Dirichlet-multinomial table is fitted
on the other five collections.  The role model fits separate outcome tables for
hidden role/non-role training rows, then mixes their probabilities using only
the held row's recovered role probability.  Smoothing strength is fixed at
eight pseudo-observations backed by the corresponding training-fold role prior.

The primary score is held codelength over all eligible pivots.  Secondary
scores are exact outcome top-1, link/no-link AUC, exact target-distance top-1,
target-distance MRR, and per-collection codelength.  The latter target metrics
use only rows with a valid external link; they do not reveal role membership to
the predictor.

## Leakage and null audits

The definition-overlap audit has two parts:

1. a static forbidden-column/source-provenance check; and
2. a collection-held exact source-signature lookup.  The endpoint is invalid
   only if the exact signature gives perfect outcome reconstruction on every
   covered held row.  High but imperfect source predictability is not itself a
   failure because the frozen endpoint asks for incremental role information.

The 2,048-world joint null permutes recovered role probabilities within held
collection and the exact source-side stratum, refits the train-fold role/outcome
mixture, and preserves the relation outcome, collection, placement, boundary,
length, recurrence and frequency opportunities.  Only strata with at least two
different scores are mobile.  The maximum codelength gain across all four routes
is retained per world.

## Frozen gate

`CMP_PARENT_01` is the priority.  A route passes only if:

* role recovery AUC is at least `.60` and saves positive held role codelength;
* at least 50 visible strict links occur in at least five collections;
* the exact source signature is not perfectly reconstructive;
* role-conditioned relation codelength gain is positive in at least four of six
  collections and positive overall;
* target-distance MRR does not decrease;
* at least 20% of eligible rows are mobile in the conditional null; and
* joint max-four `p <= .05`.

The priority route must pass, and at least three of four routes must pass, to
validate this parent-link instrument.  Failure stops before any Voynich access.
No threshold may be changed after scoring.

## Claim ceiling

A pass would show only that a domain-local latent role carries incremental
information about an editor parent-link consequence after composite encoding.
It would not establish a Voynich role, reference, time, alternative,
exclusion, POS, meaning, language, plaintext or translation.  No f84 file, row,
image, text or formal payload may be opened, parsed, retained or scored.
