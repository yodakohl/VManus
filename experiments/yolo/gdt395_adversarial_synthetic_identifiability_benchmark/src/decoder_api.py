#!/usr/bin/env python3
"""Claim-schema validation for GDT395 blind decoders."""

from __future__ import annotations

CLAIM_FIELDS = (
    "world_id", "corpus_seed", "event_id", "representation", "decoder_id",
    "entity_cluster", "lexical_cluster", "stem_cluster", "function_cluster",
    "operator_cluster", "construction_cluster", "register_variant_cluster",
    "semantic_category_cluster", "predicted_relation_target_event_id",
    "predicted_reference_target_event_id", "predicted_scope_start_event_id",
    "predicted_scope_end_event_id", "productive_component_prediction",
    "fossilized_component_prediction", "record_schema_cluster", "confidence",
)

WORLD_CLAIM_FIELDS = (
    "decoder_id", "architecture_cluster", "language_like", "notation_like",
    "codebook_like", "semantics_light_like", "confidence",
)

REPRESENTATIONS = {
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
}


def blank_claim(obs: dict, decoder_id: str, representation: str) -> dict:
    row = {k: "UNRESOLVED" for k in CLAIM_FIELDS}
    row.update({
        "world_id": obs["world_id"], "corpus_seed": obs["corpus_seed"],
        "event_id": obs["event_id"], "representation": representation,
        "decoder_id": decoder_id, "confidence": 0.0,
    })
    return row


def validate_claims(meta: dict, held_rows: list[dict], representation: str, claims: list[dict]) -> None:
    if not meta.get("oracle_blind"):
        raise ValueError("decoder lacks oracle-blind attestation")
    if representation not in REPRESENTATIONS:
        raise ValueError("unknown representation")
    if representation not in set(meta.get("supported_representations", [])):
        raise ValueError("decoder does not support representation")
    if len(claims) != len(held_rows):
        raise ValueError("claim/event count mismatch")
    expected = {r["event_id"] for r in held_rows}; seen = set()
    for row in claims:
        if set(row) != set(CLAIM_FIELDS):
            raise ValueError(f"bad claim fields {set(row) ^ set(CLAIM_FIELDS)}")
        if row["event_id"] not in expected or row["event_id"] in seen:
            raise ValueError("bad/duplicate claim event")
        seen.add(row["event_id"])
        if row["representation"] != representation or row["decoder_id"] != meta["decoder_id"]:
            raise ValueError("claim provenance mismatch")
        c = float(row["confidence"])
        if not 0.0 <= c <= 1.0:
            raise ValueError("confidence outside [0,1]")
    if seen != expected:
        raise ValueError("claim key mismatch")
