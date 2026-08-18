# GDT341 method — ordered, form-blind recipe event graphs

Date: 2026-08-18

Status: `COMPARATOR_GRAPH_FROZEN_BEFORE_VOYNICH_TUPLE_SCORING`

## Question

Can known parallel medieval recipes with different wording and abbreviation be
recovered as the same ordered anonymous event graph while unrelated recipes
are rejected? If so, does the unchanged graph retrieve formal homologues among
Recipe/Stars or Pharma records on unseen folios?

This is the ordered successor to GDT340. The shared GDT327 grammar is fixed.
Recipe/Stars and Pharma are separate targets. No field, tuple, or graph node is
assigned a universal event meaning.

## Comparator-first chronology

Stage A uses only the six GDT176 CoReMA collections. Before any GDT327
`joint_tuple_id` value is retained or scored, it freezes:

- the parallel-recipe truth rule;
- the observable graph construction;
- four fixed similarity models and selection eligibility;
- held-collection folds, controls, null, and gates;
- the selected graph representation and its exact implementation hash.

The analyst knows GDT340's target panel counts and result, but GDT341 selects no
graph feature from a Voynich association. Stage B starts only after the Stage-A
freeze is committed and pushed.

## External parallel truth — evaluation only

A comparator record is eligible when it has exactly one normalized CoReMA
English title. Two records are a positive parallel only when:

1. they belong to different collections;
2. their normalized editor titles are identical;
3. they share at least two nonempty editor concept IDs; and
4. their normalized full source surfaces have different SHA-256 hashes.

This yields source-defined semantic truth for evaluation. Titles, concepts,
roles, and surface hashes never enter a graph feature or similarity score.
Records with other titles are negatives, including size-matched negatives.

## Form-blind graph observation

Every readable record is converted to the same observation classes that can be
constructed from frozen Voynich grammar:

- complete record membership;
- ordered fields;
- ordered opaque units inside each field;
- local equality/repetition of an opaque ID, without its characters;
- record end/closure;
- cross-field continuation edges when the same opaque ID recurs;
- branch degree when one occurrence continues into two or more later fields.

CoReMA instruction containment supplies field boundaries, but instruction,
ingredient, tool, time, application, result, and closer tags are removed before
graph construction. Source forms are SHA-256 IDs and then discarded. The
graph never receives language, characters, token shape/length, English labels,
semantic roles, or adjacent lexical probabilities.

For each ordered field the frozen signature is:

`(unit-count bucket, new-ID count, returning-ID count, IDs continuing later,
branching IDs, record-end flag)`.

Repeat edges retain only source/target field quartiles and multiplicity bucket;
the identity that created an edge is discarded. This represents continuation
and branching without a lexical codebook.

## Fixed similarity family

1. `SIZE_ONLY`: record unit and field counts; baseline.
2. `UNORDERED_GRAPH`: multiset of field signatures plus repeat-edge multiset;
   strong order-free control.
3. `ORDERED_FIELD_GRAPH`: dynamic ordered alignment of field signatures,
   without repeat edges; selection eligible.
4. `ORDERED_REPEAT_GRAPH`: 70% ordered field alignment, 20% repeat-edge
   Jaccard, 10% record-size similarity; selection eligible.
5. `GLOBAL_OPAQUE_ID_CEILING`: exact opaque-ID bag Jaccard plus size; reported
   ceiling, ineligible because it cannot provide an identity-independent
   Voynich endpoint.

Weights, buckets, alignment, and tie-breaking are fixed in the design JSON.
No model is tuned to Voynich statistics.

## Stage-A scoring

Hold out one entire collection. Every eligible held recipe ranks every
single-title record in the other five collections. A correct candidate meets
the positive truth rule above. Report top-1, top-5, MRR@100, coverage, all six
folds, and hidden-oracle transition similarity after retrieval.

The hidden transition diagnostic maps CoReMA tags to MATERIAL, OPERATION,
INTERMEDIATE_STATE, APPLICATION, RESULT_CONDITION, TOOL, BRANCH, or OTHER only
after ranking. It measures whether retrieved pairs preserve event-transition
bigrams; it never trains the graph.

The selected eligible graph has highest aggregate MRR@100 with lexical
tie-break. It is supported only if it beats both `SIZE_ONLY` and
`UNORDERED_GRAPH` in aggregate MRR and top-1, improves MRR in at least four of
six collection folds, and has max-two p <= .05 under 2,048 truth-bundle
permutations within held collection × unit-count bucket × field-count bucket.

## Stage B — unchanged section-specific transfer

Only after the selected graph is public, read GDT327 with `GuardedTSV` and
reject every `f84*` selector before retention. Build two panels mechanically:

- `RECIPE_STARS_S`: section `S`, register `STARS_RECIPE_B`;
- `PHARMA_P`: section `P`, register `OTHER_A`.

A record is `(page, record_ordinal)`, a field is `(locus, field_ordinal)`, and
a unit is one opaque exact `joint_tuple_id`. Hold out every physical folio.
Rank only training records from the same panel with the frozen graph.

Because Voynich has no semantic truth, the independent target is exact formal
overlap: Jaccard overlap and occurrence recall of the held record's opaque
joint tuples in its top-ranked training record. The selected graph must beat
both `SIZE_ONLY` and `UNORDERED_GRAPH`. This asks whether an identity-free
process topology retrieves a cross-folio formal homologue; it does not call
either record a recipe parallel.

Matched controls choose candidates within exact/binned unit and field counts.
Report folio-balanced effects, coverage, 4,096 worlds, and max-family p across
the two panels and two overlap endpoints. Pharma is never pooled with
Recipe/Stars to obtain power.

## Decisions

- `ORDERED_RECIPE_GRAPH_CALIBRATED` if Stage A passes.
- `ORDERED_FORMAL_HOMOLOGY_TRANSFER_LEAD` if Stage B beats both controls on at
  least one powered panel, is positive on >=60% of folios, and max-family
  p <= .05.
- otherwise `ORDERED_GRAPH_NOT_TRANSFERABLE`,
  `NO_COMPARATOR_GRAPH_CALIBRATION`, or `INSUFFICIENT_TARGET_CAPACITY`.

## Claim ceiling

At most GDT341 can establish that an identity-free ordered record graph,
calibrated on readable parallel recipes, retrieves structurally/formally
similar records within Recipe/Stars or Pharma on unseen folios. It cannot
assign any node, field, tuple, wrapper, host, transition, or position a
semantic role or gloss; cannot identify a recipe, ingredient, operation,
state, application, result, word, sound, language, plaintext, or translation;
and cannot transfer Recipe semantics into Herbal, Astro, Bio, or other
sections. f84 is forbidden.
