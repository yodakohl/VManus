# GDT396 direct oracle-truth normalization

Status: `FROZEN_BEFORE_QUALIFICATION`.

This document is scorer/validator-side only and is never exposed to blind
decoder designers. It normalizes existing GDT395 truth; it does not redesign a
world or add semantics.

## Identity partitions

The direct fields are mapped as follows:

| GDT396 property | GDT395 oracle field / restriction |
|---|---|
| `LEXICAL_IDENTITY` | `lexical_id` |
| `SEMANTIC_ENTITY_IDENTITY` | `semantic_entity_id`, excluding `NONE` |
| `HISTORICAL_ANCESTRY` | exact `historical_stem_id` signature |
| `CURRENT_PRODUCTIVE_COMPONENT` | exact `current_morpheme_ids` signature where `productive_morphology=TRUE` |
| `FOSSIL_COMPONENT` | exact non-`NONE` `fossilized_component_ids` signature |
| `CURRENT_SHARED_MEANING` | exact non-`NONE` `current_component_semantics` signature |
| `FUNCTION_OPERATOR_CLASS` | exact non-`NONE` `function_class` |
| `CONSTRUCTION_CLASS` | `construction_id` |
| `REGISTER_REALIZATION` | `register_realization_id` |
| `SEMANTIC_CATEGORY` | exact non-`NONE` `semantic_category` signature |
| state identities | direct `state_before`, `state_after`, and their ordered pair |

Pipe values are treated as exact unordered composite signatures after sorting;
they are not silently converted into one component label.

## Binary truths

- `PRODUCTIVE_MORPHOLOGY`: direct literal `productive_morphology=TRUE`.
- `FOSSILIZED_MORPHOLOGY`: direct non-`NONE`
  `fossilized_component_ids`.
- `ENTITY_REUSE_PRESENT`: a non-`NONE` semantic entity has an earlier event in
  the same seed with the identical direct `semantic_entity_id`.
- `TEMPORAL_STATE_GATE`: membership in this frozen exact oracle predicate:

```text
function_class in {
  TEMPORAL_SCOPE, SIMULTANEOUS_SCOPE, CONDITION_SCOPE, TERMINAL_SCOPE,
  COMPLETIVE, SCOPE_OPERATOR, STATE_OPERATOR, TERMINATIVE, CONDITION_OPEN,
  CONDITION, SCOPE_CLOSE, ITERATIVE, SCOPE_GATE, SCOPE_CLOSER,
  RECURRENCE_OPERATOR, DISCOURSE, SCOPE
}
or relation_type == CONDITION
```

This is a synthetic-oracle calibration category only; it is not supplied to a
decoder and cannot be transferred to Voynich.

## Typed target truths

Every non-`NONE` target is eligible for `GENERIC_RELATION`. A typed edge is
eligible only when the oracle row has one relation type; all development rows
meet this condition, but the scorer checks it in every phase.

- `COORDINATOR_RELATION`: `function_class == COORDINATOR` and a direct target.
- `ALTERNATIVE_RELATION`: exact `relation_type` in
  `{ALTERNATIVE_TO, ALTERNATIVE, SUBSTITUTE}`.
- `REFERENCE_ANAPHORA`: exact `relation_type` in
  `{REFERS_TO, COREFERENCE, PREVIOUS_MENTION, REFERS_BACK, REF_EVENT,
  REFERENCE, INDEX_REFERENCE, CROSS_REFERENCE, continues_reference}`.
- `ENTITY_REUSE_ANTECEDENT`: all earlier events with the same direct non-`NONE`
  `semantic_entity_id`; the nearest earlier event is the primary target and all
  earlier matches are relevant for nDCG.

Target candidate policies are visible-only and frozen:

- coordinator/alternative: every other event in the same record;
- reference/entity reuse: every earlier event in the same seed;
- generic relation: every other event in the same record. Direct true targets
  outside this locality are explicit `NO_CAPACITY`, never dropped after a
  prediction is seen.

## Scope, record, and architecture

Scope truth uses the direct start/end event IDs only when both are non-`NONE`
and belong to one visible record. Other direct spans are reported as
`NO_CAPACITY_SAME_RECORD_SCOPE` rather than rewritten.

Record schema is scoreable only when every event in one visible record has the
same exact `record_schema_id`.

The only confirmatory architecture Boolean truths are direct GDT395 metadata:
`organic_evolution`, `clean_engineered_control`, and `semantics_light`.
Language/codebook/notation-like architecture labels remain diagnostics unless
an independently frozen metadata mapping supplies at least two positive and
two negative worlds.

The oracle has no component-span offsets. Morphology span/boundary output is
therefore an API/qualification diagnostic, while event Boolean status and
component-signature partitions are scoreable. Actual lexical meaning and full
historical genealogy remain `REQUIRES_EXTERNAL_GROUNDING`.
