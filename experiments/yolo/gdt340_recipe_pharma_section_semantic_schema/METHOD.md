# GDT340 method — section-specific complete-record semantic schemas

Date: 2026-08-18

Status: `COMPARATOR_ONTOLOGY_FROZEN_BEFORE_VOYNICH_TUPLE_SCORING`

## Question

Can a small event ontology for complete medieval recipes be recovered from an
observation layer comparable to the frozen Voynich grammar, and does that
unchanged instrument induce a transferable anonymous record-schema structure
inside Recipe/Stars or Pharma?

The shared GDT327 grammar is fixed. No tuple, host, wrapper, or field receives
a meaning. Recipe/Stars and Pharma are separate targets and are never pooled.

## Source-first chronology and access disclosure

Stage A uses only the six public CoReMA collections already frozen by GDT176.
The ontology, features, models, folds, gates, and comparator examples are
frozen before any GDT327 `joint_tuple_id` value is retained or scored.

Before this freeze the analyst inspected the GDT327 header and aggregate
capacity metadata (register/section/page counts), but not target tuple values,
record predictions, associations, or scores. This is therefore a
comparator-first outcome freeze with prior target-schema exposure, not pristine
target blinding.

The four comparator facsimiles listed in the source audit were inspected
directly. Those observations are explicitly external-comparator layout
observations and are not OCR, automatic vision, or Voynich evidence.

## Frozen human-readable ontology

The ontology describes events that may be present anywhere in a complete
record; it does not assign a universal field position.

| code | human-readable event class | CoReMA oracle definition |
|---|---|---|
| `MATERIAL` | named input, mixture, or dish referent | at least one `ingredient` or `dish` element |
| `OPERATION` | explicit transformation or handling event | at least one `instruction` element |
| `INTERMEDIATE_STATE` | explicit duration/state gate between operations | at least one `time` element |
| `APPLICATION` | serving/use/application event | at least one `servingTip` or `householdTip` element |
| `RESULT_CONDITION` | explicit close, readiness, or condition qualification | at least one `closer` or `dietetics` element |

`TOOL_MEDIATION` is exported as an auxiliary descriptive axis but is not one
of the five primary ontology axes. A record can carry several axes. The target
is therefore a five-bit complete-record schema, not one mutually exclusive
recipe type.

## Stage A observation boundary

The cached CoReMA TEI is parsed into complete records. Source forms are hashed
and discarded. For each record the scorer retains only:

- opaque exact unit identity;
- record membership;
- a field grouping mechanically induced by TEI instruction containment;
- unit and field counts;
- unordered within-record multiplicity;
- cross-record recurrence learned without the held collection.

The model never receives words, characters, token shapes, language, English
labels, role tags, unit order, relative position, or neighboring-token
context. Role tags are used only after feature extraction to form the five
record-level oracle bits. Instruction containment supplies a boundary, not a
field meaning.

The fixed features are log unit count, log field count, mean/SD/maximum field
size, singleton-field fraction, distinct-ID fraction, repeated-ID fraction,
mean and maximum training document frequency of the record's IDs, and mean
unordered partner degree. `STRUCTURE_ONLY` uses the first six;
`STRUCTURE_PLUS_RECURRENCE` uses all eleven. A train-prevalence Bernoulli model
is the baseline.

Each outer fold holds one entire CoReMA collection. Five independent binary
logistic models are fit within each fold. The two feature models are both
reported; no axis-specific post-hoc feature selection is allowed. The full
instrument uses `STRUCTURE_PLUS_RECURRENCE`. Fixed-prediction label
permutations preserve held collection, record-unit-count bin, and each axis's
prevalence. max-ten covers five axes times two models.

An axis is `COMPARATOR_RECOVERABLE` only if it has at least 25 positive and 25
negative records, occurs positively in at least three collections, beats the prevalence baseline
in aggregate, is positive in at least four of six folds, and has max-ten
diagnostic p <= .10. Other axes remain ontology descriptions but cannot
support a Voynich schema claim.

## Stage B — unchanged section-specific application

After the comparator result and instrument freeze are public, GDT327 is read
through `GuardedTSV`; every `f84*` selector is forbidden. Two panels are built
without consulting tuple identities for selection:

1. `RECIPE_STARS_S`: section `S`, register `STARS_RECIPE_B`;
2. `PHARMA_P`: section `P`, register `OTHER_A`.

Every complete mechanical `(page, record_ordinal)` record is retained. A
Voynich unit is one frozen exact `joint_tuple_id`; a field is the existing
`field_ordinal`. The identical eleven record features are computed, with all
recurrence statistics learned without the held physical folio. The frozen
comparator coefficients output only `MATERIAL_LIKE`, `OPERATION_LIKE`,
`INTERMEDIATE_STATE_LIKE`, `APPLICATION_LIKE`, and
`RESULT_CONDITION_LIKE` probabilities. These names denote comparator axes,
not Voynich meanings.

Blind recoverability is then tested separately inside each panel. In every
held-folio fold, the frozen comparator probability is thresholded at its
frozen CoReMA training prevalence. A `SIZE_FIELD_BASELINE` predicts that
anonymous assignment from non-held records in the same panel and exact
unit-count/field-count bins with hierarchical backoff. `EXACT_TUPLE_BAG` adds
only training-folio evidence from opaque exact tuples occurring in the held
record, with eight pseudo-trials of shrinkage toward the baseline. The
candidate is scored only where at least one tuple was seen on another folio.

This target is deliberately modest: can exact formal vocabulary recover a
comparator-defined whole-record schema assignment beyond record size and field
count? It is not semantic accuracy. Recipe/Stars and Pharma have separate
priors, fits, folds, and results. No coefficient is shared between them.

Within-panel permutations shuffle the frozen schema assignments among records
with the same physical folio, exact unit-count bin, and exact field-count bin;
max-family covers every recoverable axis and both panels. Report total gain,
bits/covered record, coverage, positive folio folds, and max-family p.

## Decisions

- `COMPARATOR_RECORD_SCHEMA_RECOVERABLE`: at least one optional axis among
  `INTERMEDIATE_STATE`, `APPLICATION`, or `RESULT_CONDITION` is recoverable.
- `SECTION_SPECIFIC_SCHEMA_RECOVERY_LEAD`: on at least one panel and one
  comparator-recoverable axis, exact tuples add positive selector-paid held
  codelength gain, at least 60% of powered folios are positive, and max-family
  p <= .05.
- otherwise `NO_BLIND_SECTION_SPECIFIC_SCHEMA_RECOVERY` or
  `INSUFFICIENT_COMPARATOR_OR_TARGET_CAPACITY`.

MATERIAL and OPERATION are expected to be nearly ubiquitous and cannot alone
pass the semantic-schema decision.

## Prior-result boundary

GDT176 remains a readable-recipe calibration. GDT224/GDT226 found coarse
position/length likeness in q13 and Stars, while GDT177 rejected independent
Q20 role support. GDT340 neither repairs nor reinterprets those field labels.
It tests a new, complete-record, optional-event endpoint with no raw position.

## Claim ceiling

At most GDT340 can show that opaque exact tuples help recover an externally
calibrated whole-record schema likeness within one section on held folios.
It cannot assign a tuple or field a role, ingredient, operation, state,
application, condition, word, sound, language, plaintext, or translation.
It cannot transfer Recipe semantics into Herbal, Astro, Bio, or any other
section. f84 is forbidden and may not be opened, parsed, retained, joined, or
scored.
