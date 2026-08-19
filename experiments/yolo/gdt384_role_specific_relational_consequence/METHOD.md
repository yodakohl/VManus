# GDT384 — role-specific relational consequence calibration

## Purpose and sequencing

GDT384 is comparator-only until its complete positive-control gate passes.  It
inherits GDT382's three instrument constraints and GDT383's domain-local,
multi-resolution role model.  It replaces GDT383's common three-event outcomes
with relations defined independently for each readable role.  No Voynich or
GDT381 target table is an input to Stage A.

The sequence is fixed:

1. freeze source provenance, relational definitions, folds, models, nulls and
   gates;
2. construct a hidden relation layer from CoReMA editor links and the exact
   frozen PCEEC2 constituent parses;
3. score the priority COORDINATOR relation first;
4. if it passes, score the remaining five already-frozen families;
5. authorize a separately frozen Voynich experiment only if the complete
   Stage-A gate passes.

If the priority relation or the complete gate fails, Stage B is not created.

## Frozen role-appropriate relations

The public `gdt384_relation_manifest.tsv` is authoritative.  Its rules do not
use a role label to define relation membership.

* `COORDINATOR` — PCEEC2 parse constituents immediately flanking the pivot
  form compatible sibling branches under one local attachment container.  A
  one-level `CONJP` nesting is allowed.  Operand homology is based on normalized
  constituent class, never on the pivot word or POS.
* `ALTERNATIVE_OR` — CoReMA elements share one editor-linked parent instruction
  with at least one other child carrying a distinct editor concept ID.  This
  establishes sibling branches but not their semantics.  The PCEEC sibling
  relation is retained only as a partial sensitivity because a constituent
  parse does not annotate mutual exclusion.
* `REF_ANAPHORA` — a CoReMA element has an explicit parent-instruction link to
  a strictly earlier instruction in the same recipe.  This is backward, not
  downstream-only.
* `UNTIL_STATE_GATE` — in CoReMA, an explicitly parented element is followed at
  a variable horizon by the first element outside that parent instruction;
  in PCEEC2, the pivot lies inside a PP/CP/subordinate-IP scope with a strict
  right edge followed by material in the containing record.  Scope length is
  a measured relation attribute and is not fixed at three events.
* `POLARITY_EXCLUSION` — CoReMA concept identity is reused in contrasting
  parent contexts; PCEEC2 supplies only a partial clause-attachment
  sensitivity.  Neither annotation is called logical inversion.
* `FUNCTION_WORD` — PCEEC2 parse topology supplies a cross-constituent bridge
  relation and training-fold parent-category breadth.  It is tested especially
  strongly for overlap with frequency and placement because these channels
  also enter role recovery.

Curious Cures, Harleian and Quinte Essence remain role-recovery domains but do
not supply relational gold: their existing oracle is lexical, not a parse,
coreference graph, scope graph, or inverse-state annotation.  No proximity or
string heuristic upgrades them to gold.

## Observation boundary and role model

The scored `X` layer is exactly the frozen GDT382 oracle-blind composite
observation.  Five resolutions are evaluated simultaneously:

1. opaque host-like identity;
2. complete rendered group;
3. wrapper/boundary/position construction;
4. composite joint state; and
5. short local construction span ending at the pivot.

Frequency, recurrence, line/field and record-relative position,
boundary/closure, previous state and record length remain candidate grammar
channels.  The primary hierarchy includes them as evidence; conditioned-
nuisance and omitted variants are mandatory controls.  Exact-joint-only and
strict universal-coefficient models remain baselines.

Every role score is produced out of collection: the held collection contributes
neither opaque realization counts nor role labels.  Relation models use only
the cross-fitted role score and an independently frozen source baseline.

## Definition-overlap audit

For each relation, a source-only model receives every licensed pivot/pre-pivot
observation and grammar channel but no hidden parse, parent, concept or
post-pivot relation field.  The relation is ineligible if source-only held AUC
exceeds `0.65`, or if a deterministic source signature reconstructs membership
above `0.65`.  The audit is performed before thresholding role gain.

The role-plus-relation model must improve held codelength over this source-only
baseline.  It may not use the role oracle at test time; only the fold-trained
role probability is exposed.

## Folds, null and gates

CoReMA folds are its six editor collections.  PCEEC2 folds are deterministic
source-file blocks, preserving whole parsed records.  A relation with only one
gold corpus is explicitly a single-domain positive control and must be stable
in at least four powered held collection blocks.  This is sufficient for
instrument calibration only, never for a semantic claim.

The fixed 2,048-world joint max-family null permutes hidden role labels within
domain, held collection, record-length bin, pivot-position bin and boundary
state, then rebuilds the fold-trained role contribution while retaining the
relation gold.  It charges all six roles, relation variants, resolutions,
channel treatments and horizons.  PCEEC constituent label granularity and
CoReMA parent definitions are fixed and are not searched.

A role-specific consequence passes only if:

* the GDT383 hierarchy has held role AUC `>= 0.80`, positive role codelength,
  and beats exact-joint by `.02` and strict universal by `.10`;
* the relation has at least 50 positive and 50 negative eligible occurrences;
* source-only and deterministic-overlap AUC are both `<= .65`;
* adding the cross-fitted role score saves held relation codelength, improves
  relation AUC by at least `.02`, is positive in every powered gold corpus, and
  is positive in at least four held collection blocks; and
* joint max-family `p <= .05`.

COORDINATOR must pass first.  Full Stage A additionally requires all six roles
to pass their primary consequence and all 42 GDT383 realization ceilings to
remain passed.  No role-specific threshold may be lowered.

## Conditional target contract

Only a published complete Stage-A pass can authorize a new target freeze.
Such a target would use the anonymous name `LATENT_ROLE_A`, register-local
realizations, and the frozen homologous relation test.  It would not reuse or
inspect GDT381 memberships, realizations, thresholds or scores.  No comparator
role word transfers to Voynich.

## Claim ceiling

A comparator pass establishes only that the repaired instrument can recover a
known role and its independent relation after composite encoding.  It does not
establish a Voynich function, role, POS, operator, language, plaintext or
translation.  F1, AQ/contact, PAGE_HOST substring mining, exact-tuple semantic
routes and GDT345–347 remain closed.  No f84 file, row, image, text or formal
payload may be opened, parsed, retained or scored.
