# GDT342 method — comparator-first anonymous entity-flow graphs

Date: 2026-08-18

Status: `COMPARATOR_ENTITY_FLOW_FROZEN_BEFORE_SCORING`

## Question

Can wording-distinct parallel medieval recipes be recovered from the ordered
flow of recurring entities after every editor concept identifier has been
replaced by a record-local anonymous symbol? If that representation first
calibrates on readable comparators, does the identical equality/flow
representation transfer to exact GDT327 tuples on held Recipe/Stars and Pharma
folios?

This is a genuinely different successor to GDT341. GDT341 reduced identities
to field-level counts and discarded which anonymous entity made which edge.
GDT342 retains the complete within-record equality/incidence topology while
discarding global identity and every lexical or semantic label.

## Comparator-first chronology

Stage A uses only the six hash-frozen CoReMA collections. Before any comparator
score and before any GDT327 target value is retained, the experiment freezes:

- the external parallel-recipe truth rule;
- the record-local anonymization rule;
- the field, entity-path, merge/split, continuation, and closure graph;
- one fixed entity-flow model and three required controls;
- held-collection folds, null, gates, and tie breaking;
- the prospective target transfer endpoint.

Stage B is forbidden unless Stage A passes. If it passes, the exact selected
representation and implementation are committed before GDT327 is opened.

## External truth — evaluation only

A readable record is eligible when it has exactly one normalized editor title.
Two records are a positive parallel only when they:

1. are in different collections;
2. have the same normalized editor title;
3. share at least two nonempty editor concept IDs; and
4. have different normalized full-source hashes.

This is the unchanged GDT341 truth rule. Titles and global concept IDs are used
only to decide correctness after ranking. They never enter the anonymous graph.

## Anonymous observation layer

For each non-title CoReMA element, the source layer supplies element order,
instruction containment, and optionally an editor concept ID.

- Each distinct nonempty concept ID is mapped, within that record only, to
  `E1`, `E2`, ... in order of first occurrence.
- The mapping is freshly restarted in every record. `E1` in two records has no
  shared identity.
- An element without a concept ID receives a unique record-local singleton and
  can never create a recurrence edge.
- Concept names, IDs, source forms, characters, roles, and word lengths are
  absent from the graph and all exported record-level artifacts.
- Instruction containment creates ordered fields. An instruction and its
  contained elements share one field; other exterior elements form ordered
  singleton fields. The semantic type of a field is removed.

This leaves an ordered bipartite incidence graph between fields and anonymous
entity nodes. It preserves only:

- entity recurrence and multiplicity;
- immediate continuation and return after a gap;
- merge-like fields with multiple incoming recurring entities;
- split/reuse-like entities occurring in multiple later fields;
- ordered field transitions and record closure.

“Merge” and “split” are graph motifs, not claims about physical ingredients or
operations.

## Frozen graph representation

Each field has a nine-coordinate signature:

`(unit count, distinct entity count, new entities, immediate continuations,
returns after a gap, entities used later, merge flag, split/reuse count,
record closure)`.

Counts are clipped to 1–4, with zero retained as zero. Each adjacent field pair
has a transition signature containing source/target sizes, shared entities,
new entities, ended entities, returning entities, merge flag, and split/reuse
count. Each entity has a path signature containing occurrence-count bucket,
first/last field quartiles, maximum-gap bucket, immediate-continuation count,
return flag, and final-field presence. Identity labels are discarded after
these paths are built.

The sole eligible model is:

`ANON_ENTITY_FLOW = .35 ordered-field alignment + .20 ordered-transition
alignment + .20 entity-path multiset Jaccard + .15 flow-edge multiset Jaccard
+ .10 record-size similarity`.

## Required controls

1. `SIZE_ONLY`: total units and fields.
2. `ORDER_ONLY`: ordered field sizes and closure, with all equality removed.
3. `UNORDERED_INCIDENCE`: field-degree and entity-degree multisets plus size,
   retaining recurrence capacity while discarding order and trajectories.
4. `RAW_OPAQUE_WORD_IDENTITY`: exact source-form hashes plus size. Characters
   and words are never exported, but this is a strong ordinary-word control.
5. `GLOBAL_CONCEPT_ID_CEILING`: exact editor-concept overlap plus size. This is
   a truth-proximal oracle ceiling and is never selection eligible.

The entity-flow model must beat the first four controls. The ceiling measures
how much recoverable parallel identity exists when global normalization is
allowed.

## Stage-A scoring and null

Hold out one entire collection. Each eligible held record ranks every
single-title record in the other five collections. Report top-1, top-5,
MRR@100, and all six folds.

The fixed 2,048-world null moves complete truth bundles within held collection
× unit-count bucket × field-count bucket while keeping every ranking fixed.
Stage A passes only when `ANON_ENTITY_FLOW`:

- beats every required control in aggregate MRR and top-1;
- beats every required control in at least four of six held collections; and
- has inclusive null p <= .05 for its MRR gain over the best control.

No post-score weight, bucket, feature, or threshold changes are allowed.

## Frozen prospective Stage B

Only after a public Stage-A pass, stream-read GDT327 with a raw-selector guard
that rejects every `f84*` row before parsing the remainder. Recipe/Stars and
Pharma remain separate panels.

Each exact `joint_tuple_id` is an opaque candidate entity ID. It is never
merged, decomposed, or assigned a role. Within each record, tuple IDs are
renamed by first occurrence exactly like CoReMA concepts.

The primary held-folio endpoint is next-field persistence. For each distinct
opaque ID present in field `i`, predict whether the same ID occurs in field
`i+1`. The fixed nuisance model uses panel, record field count, field quartile,
current field size, prior within-record occurrence count, and training-folio
global frequency. The flow model adds only past-observable anonymous state:
immediate prior continuation, fields since last occurrence, current
co-occurring recurrent count, and prior split/reuse count. It must improve
held-folio log loss over nuisance and over a training-only exact-ID survival
table, be positive in >=60% of powered folios in one panel, and survive a
4,096-world within-record identity permutation preserving field sizes and
record-local ID multiplicities. Panels are never pooled for power.

This prospective endpoint tests persistent formal identity flow. It does not
establish that a tuple denotes an entity.

## Decisions

- `ANONYMOUS_ENTITY_FLOW_CALIBRATED`
- `ANONYMOUS_ENTITY_FLOW_NOT_CALIBRATED`
- `OPAQUE_TUPLE_FLOW_TRANSFER_LEAD`
- `OPAQUE_TUPLE_FLOW_NOT_TRANSFERABLE`
- `INSUFFICIENT_TARGET_CAPACITY`

## Claim ceiling

At most, GDT342 can establish that a record-local anonymous equality-flow
graph recovers wording-distinct recipe parallels and that exact opaque Voynich
tuples exhibit a comparable held-folio persistence law in Recipe/Stars or
Pharma. It cannot establish that a tuple is an ingredient, operation, state,
object, word, morpheme, code value, or semantic entity; cannot merge tuples or
assign glosses; cannot identify a language, plaintext, or translation; cannot
export the schema to Herbal, Astro, Bio, or other sections; and cannot access
f84.
