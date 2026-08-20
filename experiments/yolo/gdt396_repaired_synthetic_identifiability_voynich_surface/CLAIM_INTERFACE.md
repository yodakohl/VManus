# GDT396 blind claim interface V2

Status: `REGISTERED_BEFORE_DECODER_DEVELOPMENT`.

Decoder authors receive this document, `src/decoder_api_v2.py`, and blind
observation packets only. They may not inspect GDT395 world sources, designs,
oracles, codebooks, genealogies, scorer code, sibling decoders, sibling claims,
or any Voynich source.

## Observation boundary

Every loaded observation has opaque `world_id`, `corpus_seed`, `surface_channel`,
`page_id`, `paragraph_id`, `record_id`, `line_id`, `event_id`, global
`event_index`, within-record `record_event_ordinal`, `group_index`, the visible
surface, source separators, register/hand IDs, layout role, position bins, and
ambiguous-boundary flag. Identifiers expose equality and physical membership
only.

For `FREE_SURFACE`, the surface is an opaque Unicode group. For
`VOYNICH_SURFACE`, it is a tuple of integer atom positions in `0..23`. A
decoder receives one surface channel in a fresh process and never receives the
cross-channel mapping.

## Decoder API

```python
API_VERSION = 2
DECODER_META: dict
def fit(train_rows: list[dict]) -> dict: ...
def decode(model: dict, held_rows: list[dict], representation: str) -> dict[str, list[dict]]: ...
def classify_world(model: dict) -> list[dict]: ...
```

The model must be canonical-JSON-safe. The runner hashes it immediately after
fit and verifies that every held decode leaves it unchanged. All learning,
thresholds, vocabularies, and components use the supplied training rows only.

`DECODER_META` contains `api_version`, `decoder_id`, `designer_model`,
`method_family`, `oracle_blind`, `supported_representations`,
`supported_claim_kinds`, `max_rank_by_claim_kind`,
`fit_scope=TRAIN_ONLY_WORLD`, and `transductive_within_held_seed`.

Permitted representations are:

`FULL_GROUP, HOST_LIKE, COMPOSITE_STATE, INFERRED_COMPONENTS,
CONSTRUCTION_SPAN, RECORD_TOPOLOGY, MULTI_RESOLUTION`.

`HOST_LIKE` is a decoder-inferred recurrent component, not an externally
provided parser field. `COMPOSITE_STATE` uses visible group plus licensed
layout/boundary metadata. `MULTI_RESOLUTION` may combine the other levels.

## Normalized outputs

Every row starts with the common key:

```text
schema_version phase run_id world_id corpus_seed surface_id representation_id
decoder_id method_variant property_id
```

`phase` is `DEVELOPMENT`, `QUALIFICATION`, or `CONFIRMATION`;
`method_variant` is `PRIMARY`, `MULTI_CONSTRAINT`, or `SCALAR_BOTTLENECK`.
Claim status is explicitly `RESOLVED`, `ABSTAIN`, or `UNSUPPORTED`. All class
IDs and relation subtype IDs are anonymous decoder-local identifiers. There
are no pipe-delimited sets.

The exact headers and enums are executable in `src/decoder_api_v2.py`.

### Partition and binary claims

`partition_claims` adds:

```text
unit_type unit_id claim_status cluster_id confidence
```

It covers lexical identity, semantic-entity co-identity, historical ancestry,
currently productive shared components, fossilized shared components, current
shared meaning, function/operator class, construction, register realization,
semantic category, and before/after/transition state identity. These are
generic requested partitions; no readable class names are exposed.

`binary_claims` adds:

```text
unit_type unit_id claim_status predicted_bool confidence
```

It covers event-level productive morphology, fossilized morphology,
temporal/state-gate candidacy, and recurring-entity reuse.

### Ranked target claims

`target_queries` emits exactly one row per attempted source/property, including
abstentions:

```text
source_event_id candidate_set_id claim_status predicted_target_count confidence
```

Its child `target_ranks` rows are:

```text
source_event_id candidate_set_id target_rank target_event_id target_score type_id
```

Target properties are `GENERIC_RELATION`, `COORDINATOR_RELATION`,
`ALTERNATIVE_RELATION`, `REFERENCE_ANAPHORA`, and
`ENTITY_REUSE_ANTECEDENT`. Candidate universes are derived from visible
record/line structure, never from oracle-positive anchors. Ranks are one-based,
contiguous, nonduplicated, and nonincreasing in score.

### Scope and morphology

`scope_claims` adds:

```text
source_event_id claim_status scope_present predicted_start_event_id
predicted_end_event_id scope_type_id confidence
```

Both positive endpoints must exist in the same record and the start ordinal
cannot follow the end ordinal.

`morphology_claims` adds:

```text
event_id component_id start_offset end_offset morphology_status claim_status
rank confidence
```

Offsets are half-open atom offsets in the selected surface.
`morphology_status` is exactly `CURRENTLY_PRODUCTIVE`, `FOSSILIZED`, or
`NO_COMPONENT_CLAIM`. Multiple ranked analyses are allowed. Because the GDT395
oracle does not locate component spans, span recovery is a qualification/API
diagnostic unless a direct frozen truth exists; event-level productive/fossil
status and component co-identity are the primary scored endpoints.

### Record and architecture claims

`record_partition_claims` adds one row per visible record:

```text
record_id claim_status record_schema_cluster_id confidence
```

Architecture is evaluated per seed, surface, and representation. The
partition table predicts one anonymous `WORLD_ARCHITECTURE` class; the binary
table may predict only generic `LANGUAGE_LIKE`, `NOTATION_LIKE`,
`CODEBOOK_LIKE`, `ORGANIC_EVOLUTION_LIKE`, `CLEAN_ENGINEERED_LIKE`, or
`SEMANTICS_LIGHT_LIKE` flags whose truth is frozen in world metadata.

## Validation

The runner and independent validator enforce exact provenance, key uniqueness,
finite scores, descending contiguous ranks, fixed rank caps, legal event and
record IDs, legal target universes, same-record scope spans, legal morphology
offsets/statuses, output-table field equality, deterministic reruns, model
immutability, and absence of readable/oracle labels in anonymous IDs.
