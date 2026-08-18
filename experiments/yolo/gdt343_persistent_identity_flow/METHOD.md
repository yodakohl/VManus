# GDT343 method — persistent identity plus flow

Date: 2026-08-18

Status: `COMPARATOR_PERSISTENT_IDENTITY_FLOW_FROZEN_BEFORE_SCORING`

## Question

Once lexical meaning is hidden but normalized entity identity remains stable
across records and collections, does ordered entity flow add held-collection
parallel-recipe retrieval beyond identity alone? Only a readable-comparator
pass can authorize the exact analogue on GDT327 Recipe/Stars and Pharma.

GDT342 showed that record-local anonymous flow carries signal but cannot
replace cross-record identity. GDT343 tests the nested question the prior design
could not answer: `persistent identity + flow` versus the same persistent
identity without flow.

## Comparator-first chronology

Stage A uses only the six hash-frozen CoReMA collections. Before scoring and
before any GDT327 value is retained, this file and the design JSON freeze:

- the unchanged parallel truth;
- global anonymous identity construction;
- exactly three primary models A/B/C;
- the identity-aware flow augment and its fixed weight;
- held-collection folds, null, decision gate, and tie breaking;
- the prospective held-folio tuple-persistence endpoint.

Stage B is forbidden unless C passes. If it passes, the exact comparator result,
representation, and implementation are committed and pushed before GDT327 is
opened.

## External truth — evaluation only

The GDT341/GDT342 truth rule is unchanged. A record has exactly one normalized
editor title. A positive candidate is in another collection, has the same
normalized title, shares at least two nonempty concept IDs, and has a different
normalized source-surface hash.

Titles and semantic labels are evaluation-only. Concept IDs are allowed only
through a deterministic salted hash. The hash is stable across every record and
collection, but neither the source ID nor its name is exported.

## Frozen observation and flow

Every non-title CoReMA element belongs to its ordered instruction/exterior
field. A nonempty editor concept ID becomes one globally consistent opaque
20-hex identity. A missing concept becomes a unique local singleton and cannot
create cross-record or within-record recurrence.

The record retains:

- a multiset of global opaque concept identities;
- ordered fields and global identities present in each field;
- for each global identity, occurrence fields, immediate continuation, return
  after gaps, first/last quartile, future reuse, and closure participation;
- identity-specific flow edges between successive occurrence fields;
- anonymous merge/split/reuse and closure field motifs.

No editor label, source concept ID, source word, character, role name, or word
length enters C.

## Fixed A/B/C models

### A — `RAW_OPAQUE_WORD_IDENTITY`

Diplomatic source tokens are independently salted and compared as multisets:

`.85 token multiset Jaccard + .15 record-size similarity`.

CoReMA `commodity=Q...` attributes and English labels are forbidden. This is
the independently reconstructed GDT342 control.

### B — `GLOBAL_ANON_CONCEPT_IDENTITY`

`.75 concept multiset Jaccard + .15 concept set Jaccard + .10 record-size
similarity`.

This is the mandatory nested baseline.

### C — `GLOBAL_ANON_IDENTITY_PLUS_FLOW`

`B + .10 FLOW_AUGMENT`, where:

`FLOW_AUGMENT = .40 same-identity path similarity + .30 identity-specific
flow-edge Jaccard + .20 ordered field identity alignment + .10 anonymous
field-motif alignment`.

All components lie in [0,1]. The `.10` coefficient, component weights, count
clipping, alignment, and lexical tie break are fixed. No weight grid or target-
driven fitting is permitted.

## Stage-A evaluation

Hold out one complete collection. Every eligible held record ranks all
single-title records in the other five collections. Report top-1, top-5,
MRR@100, and all six folds.

C is calibrated only if it:

- exceeds B in aggregate MRR and top-1;
- exceeds B in at least four of six held collections; and
- has inclusive p <= .05 under 4,096 complete truth-bundle permutations within
  held collection × unit-count bucket × field-count bucket.

A is reported as an ordinary lexical control but is not part of the nested C>B
gate. The null holds every A/B/C ranking fixed and moves the complete external
truth bundle; there is one tested augment, so no model-family selector exists.

## Frozen prospective Stage B

Only after a public Stage-A pass, use a guarded raw-selector loader that rejects
every `f84*` GDT327 row before parsing any other field. Recipe/Stars and Pharma
are separate panels and are never pooled.

Each exact `joint_tuple_id` is a globally persistent opaque candidate identity.
Tuple IDs are not merged, decomposed, aligned by glyph similarity, or assigned
a role.

For each distinct tuple present in field `i`, the binary target is whether that
same tuple occurs in field `i+1`. Whole physical folios are held out.

- B is a training-only exact-tuple survival table with Jeffreys smoothing plus
  fixed nuisance strata: panel, field quartile, record field-count bucket, and
  current field-size bucket.
- C adds the exact comparator-licensed past-only flow state: immediate prior
  continuation, fields since prior occurrence, prior occurrence-count bucket,
  number of co-present returning identities, prior future-reuse opportunity,
  and current-field closure distance.

The low-capacity C model is a fixed-ridge logistic model whose feature schema
and regularization are frozen here; coefficients and standardization are
learned only from non-held folios. C must gain held log-loss bits over B, be
positive on >=60% of powered folios in one panel, and survive 4,096 within-
record identity-path permutations preserving field sizes, record-local tuple
multiplicities, and the B exact-identity table. Report both panels separately.

This tests formal persistence, not whether a tuple truly denotes an entity.

## Decisions

- `PERSISTENT_IDENTITY_FLOW_CALIBRATED`
- `PERSISTENT_IDENTITY_FLOW_NOT_CALIBRATED`
- `EXACT_TUPLE_IDENTITY_FLOW_TRANSFER_LEAD`
- `EXACT_TUPLE_IDENTITY_FLOW_NOT_TRANSFERABLE`
- `INSUFFICIENT_TARGET_CAPACITY`

## Claim ceiling

At most GDT343 can establish that identity-specific order/return/merge/split
features add to persistent opaque identity on readable parallel recipes and,
if prospectively transferred, that exact GDT327 tuple identity has a comparable
held-folio persistence law in Recipe/Stars or Pharma. It cannot establish that
a tuple is an entity, ingredient, operation, state, word, morpheme, or code
value; cannot merge tuples or assign a gloss; cannot identify a language,
plaintext, or translation; cannot transfer to Herbal, Astro, Bio, or other
sections; and cannot access f84.
