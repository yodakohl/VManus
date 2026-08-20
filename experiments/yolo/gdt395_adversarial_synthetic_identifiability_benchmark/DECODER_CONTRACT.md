# GDT395 blind decoder contract

Inspect only the supplied observation packets and this contract. Do not inspect
world generator source, design documents, manifests revealing family, oracle,
codebook, genealogy, other decoder outputs, or any Voynich file.

Your decoder must operate without readable words or externally supplied labels.
It may exploit visible equality, strings, separators, records, lines, layout,
register/hand, recurrence, and context. It must emit anonymous predictions at
each supported representation level:

`FULL_GROUP, HOST_LIKE, COMPOSITE_STATE, INFERRED_COMPONENTS,
CONSTRUCTION_SPAN, RECORD_TOPOLOGY`.

For each event emit:

`world_id, corpus_seed, event_id, representation, decoder_id,
entity_cluster, lexical_cluster, stem_cluster, function_cluster,
operator_cluster, construction_cluster, register_variant_cluster,
semantic_category_cluster, predicted_relation_target_event_id,
predicted_reference_target_event_id, predicted_scope_start_event_id,
predicted_scope_end_event_id, productive_component_prediction,
fossilized_component_prediction, record_schema_cluster, confidence`.

Use `UNRESOLVED` rather than inventing unsupported claims. Also emit one
world-level row per representation with an anonymous architecture class and
confidence. A decoder may infer components but must not name meanings.
