# GDT344 method — grammar transition paths above atomic joint tuples

Date: 2026-08-19

Status: `FROZEN_BEFORE_FORMAL_AND_COMPARATOR_SCORING`

## Question and scope

Do different exact GDT327 joint-tuple sequences realize a transferable grammar
of formal coordinate transitions, and can such path types later align with
complete-record event-path classes calibrated on readable recipes?

The exact `joint_tuple_id` remains atomic. GDT344 never factors PAGE_HOST,
merges tuples, compares glyph strings, or assigns a tuple meaning. Only the two
pre-existing section-specific panels are eligible:

- Recipe/Stars: section S, register `STARS_RECIPE_B`;
- Pharma: section P, register `OTHER_A`.

No Herbal, Astro, Bio, or other section enters any score. Every source loader
rejects `f84*` selectors before parsing the rest of a row.

## Stage A — formal transition paths

The allowed page set is frozen from the GDT340 Recipe/Pharma record inventory.
The f84-free GDT327 interlinear is joined one-to-one to GDT278 coordinates by
`(page,locus,group_index)`. File order supplies physical page order. Every
adjacent pair on one page is exported; record-boundary edges are retained as a
separate reset class rather than interpreted as process continuation.

For source event `a` and target event `b`, an exact transition signature keeps:

- `local_frame(a) -> local_frame(b)`;
- `inner_d(a) -> inner_d(b)`;
- `right_family(a) -> right_family(b)`;
- `dy_closure(a) -> dy_closure(b)`;
- `b3(a) -> b3(b)`;
- canonical wrapper-state transition;
- same/next/reset/skipped field order;
- field boundary, record boundary, and physical-line reset.

The coarse shape signature replaces each nominal value pair by
`STAY_NONE`, `STAY_VALUE`, `ADD`, `DROP`, or `SWITCH`, while preserving all
boundary/order flags. It is a second predeclared resolution, not a selected
post-hoc recoding.

Supported renderer effects are nuisance. An observed `s` at physical line
start and `q` immediately after DY are canonicalized to renderer-nuisance
states before wrapper transitions are formed. No semantic value is assigned to
the remaining wrappers, DY, or B3.

### Held-folio prediction

The target is the next exact formal coordinate. Every score also includes the
unchanged GDT336 target-tuple-within-coordinate placement code, so comparisons
measure grammar above the atomic tuple rather than replacing it.

Four coordinate models are fixed:

1. `PLACEMENT`: panel/register, target line entry, within-field position, line
   quartile, boundary scope, and renderer nuisance;
2. `EXACT_PREDECESSOR`: placement plus the exact preceding atomic tuple;
3. `PATH_SHAPE`: placement plus the preceding coarse coordinate state and
   coarse transition/boundary context;
4. `PATH_VALUE`: placement plus the preceding exact coordinate state and exact
   transition/boundary context.

Context tables are Dirichlet-shrunk to `PLACEMENT`. Concentration is selected
from `{8,32,128,512}` by inner leave-one-training-folio-out scoring separately
for every outer model/fold. The GDT336 exact-tuple placement component uses its
already published held-folio concentration and is identical across all four
models.

Test edges are scored only when the target coordinate and exact target tuple
exist on another training folio in the same panel. Report all edges,
within-record edges, field-boundary edges, record resets, and the decisive
subset whose exact `(source_tuple,target_tuple)` pair is unseen in training.

An abstract path is supported only if one predeclared path model:

- beats both `PLACEMENT` and `EXACT_PREDECESSOR` in held codelength;
- is positive over `EXACT_PREDECESSOR` in at least 60% of powered folios in
  each panel;
- gains over `PLACEMENT` on unseen exact tuple-pair edges; and
- has max-two inclusive p <= .05 under 4,096 fixed-prediction permutations.

The permutation moves complete target-coordinate labels within held folio ×
boundary scope × target placement × renderer-nuisance strata. It preserves the
observed marginal target and opportunity structure but does not refit models;
its p-value is therefore an alignment diagnostic, not a globally exact model-
selection test.

## Stage B — readable-recipe event-path calibration

Stage B begins from the six frozen CoReMA collections and does not inspect any
new Voynich value. Editor roles create evaluation-only complete-record event
paths. MATERIAL is ingredient/dish, OPERATION is instruction,
INTERMEDIATE_STATE is time, APPLICATION is serving/household use, and
RESULT_CONDITION is closer/dietetics. Records containing MATERIAL and OPERATION
are assigned one of five optional-path classes:

- `BASIC_MO`;
- `MO_STATE_ONLY`;
- `MO_APPLICATION_ONLY`;
- `MO_RESULT_ONLY`;
- `MO_MULTI_OPTIONAL`.

Words, concept names, and role labels are hidden from model features. Globally
anonymous concept IDs are used only as opaque equality relations. Shared
observation features are record/field sizes, ordered field-size changes,
identity recurrence, adjacent-field overlap, return, merge, split/reuse, and
closure. `SHAPE_ONLY` is the required baseline; `IDENTITY_FLOW_TOPOLOGY` adds
only the latter anonymous relations.

Fixed-ridge multinomial models hold one complete collection out. The topology
instrument calibrates only if it improves aggregate held log-loss over shape,
is positive in at least four of six collections, and has inclusive p <= .05
under 4,096 class-bundle permutations within collection × unit-count bucket ×
field-count bucket.

## Stage C — gated section-specific alignment

Stage C is forbidden unless both Stage A and Stage B pass. If authorized, the
frozen comparator model assigns a complete-record event-path-likeness class to
each Recipe/Stars and Pharma record from opaque exact-tuple recurrence and
record structure. These are comparator likeness labels, not Voynich meanings.

Within each panel and held physical folio, a baseline using record shape and
the GDT336 placement summary predicts that fixed class. `FORMAL_PATH_BAG` adds
only 64 fixed SHA-256 bins of the Stage-A transition signatures. The two panels
are never pooled. A lead requires positive held bits, positive folds on at
least 60% of powered folios, and 4,096-world within-panel max-two p <= .05.

No field or tuple receives MATERIAL, OPERATION, STATE, APPLICATION, RESULT, or
any other gloss.

## Decisions

- `ABSTRACT_GRAMMAR_TRANSITION_PATHS_SUPPORTED`
- `NO_TRANSFERABLE_GRAMMAR_TRANSITION_PATH`
- `COMPARATOR_EVENT_PATH_CALIBRATED`
- `COMPARATOR_EVENT_PATH_NOT_CALIBRATED`
- `SECTION_SPECIFIC_EVENT_PATH_ALIGNMENT_LEAD`
- `NO_SECTION_SPECIFIC_EVENT_PATH_ALIGNMENT`
- `INSUFFICIENT_CAPACITY`

## Claim ceiling

At most GDT344 can establish a held-folio recurrence law over changes between
atomic formal tuples and, behind an independent readable-comparator gate, a
record-level structural likeness to a small recipe event-path class. It cannot
merge tuples, factor PAGE_HOST, assign a tuple or field a semantic role, or
infer a word, morpheme, sound, language, plaintext, translation, or f84 result.
