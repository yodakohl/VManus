# GDT395 isolated world-design contract

You are designing exactly one hidden writing system. Do not inspect any other
GDT395 world, decoder, oracle, result, Voynich file, or Voynich hypothesis.

Implement one deterministic Python module in your assigned `worlds/wNN_*`
directory. It must export:

```python
WORLD_META: dict
def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]
```

The return object has exactly four lists: `observations`, `oracle`, `codebook`,
and `genealogy`. Use only the Python standard library. For a fixed seed and
target size, serialized content must be deterministic.

## Observation rows

Every visible event has these fields and no hidden truth:

`world_id, corpus_seed, event_id, page_id, paragraph_id, record_id, line_id,
event_index, group_index, visible_group, separator_before, separator_after,
register_id, hand_id, layout_role, line_position_bin, record_position_bin,
ambiguous_boundary`.

Use hierarchical separators from `{PAGE, PARAGRAPH, RECORD, LINE, FIELD,
SPACE, JOIN, NONE}`. `visible_group` uses an invented symbol inventory and must
not copy Voynich strings. IDs may expose equality/physical membership but not
semantic names.

## Oracle rows

There is exactly one oracle row per observation event with the same event key
and these hidden fields:

`domain_id, activity_id, lexical_id, semantic_entity_id, semantic_category,
function_class, relation_type, relation_target_event_id, state_before,
state_after, historical_stem_id, current_morpheme_ids,
fossilized_component_ids, construction_id, scope_start_event_id,
scope_end_event_id, record_schema_id, register_realization_id,
productive_morphology, current_component_semantics, genealogy_stage`.

Use `NONE` when a property does not apply. Multiple values are pipe-separated
in stable sorted order. Do not put hidden names in any observation field.

## Codebook and genealogy

Codebook rows must make the final system exactly auditable after unblinding:
`lexical_id, semantic_entity_id, semantic_category, historical_stem_id,
canonical_hidden_form, final_realization_rules, irregularity_flags`.

Genealogy rows must record each ordered evolution event:
`stage, rule_id, process_type, input_ids, output_ids, conditioning,
currently_productive, notes`.

At least six distinct evolution stages are required unless your assigned world
is explicitly a clean or semantics-light control. Organic worlds should use
frequency-driven shortening, analogy, merger/split, bleaching, fossilization,
polyfunctionality, suppletion/exceptions, and register/school divergence where
appropriate. Avoid a simple one-prefix/one-stem/one-suffix truth table.

## Corpus and layout

Create pages, paragraphs, records, physical lines, hierarchical separators,
line resets, recurring constructions, joined/detached realizations,
position-dependent rendering, at least three registers and two hands, and
ambiguous observation boundaries. Corpus seeds must differ in content and
event realization while using the same historical system.

Each seed should reach `target_events` to within one completed record. Preserve
realistic skewed recurrence and register distributions. Do not pad by blindly
copying one record.

## Required metadata

`WORLD_META` contains:

`world_id, title, broad_family, practical_domain, semantics_light,
organic_evolution, clean_engineered_control, adversarial_pair_id,
carrier_profile, alphabet, registers, hands, evolution_processes,
generator_schema`.

Do not include commentary about Voynich. Add a brief `DESIGN.md` explaining the
hidden system and intended adversarial confounds; this is sealed from decoders.
