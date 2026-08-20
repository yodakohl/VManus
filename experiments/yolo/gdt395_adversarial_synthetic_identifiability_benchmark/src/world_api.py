#!/usr/bin/env python3
"""Shared schema helpers for isolated GDT395 world modules."""

from __future__ import annotations

import hashlib
import json
import random
from typing import Iterable

OBS_FIELDS = (
    "world_id", "corpus_seed", "event_id", "page_id", "paragraph_id",
    "record_id", "line_id", "event_index", "group_index", "visible_group",
    "separator_before", "separator_after", "register_id", "hand_id",
    "layout_role", "line_position_bin", "record_position_bin",
    "ambiguous_boundary",
)

ORACLE_FIELDS = (
    "world_id", "corpus_seed", "event_id", "domain_id", "activity_id",
    "lexical_id", "semantic_entity_id", "semantic_category", "function_class",
    "relation_type", "relation_target_event_id", "state_before", "state_after",
    "historical_stem_id", "current_morpheme_ids", "fossilized_component_ids",
    "construction_id", "scope_start_event_id", "scope_end_event_id",
    "record_schema_id", "register_realization_id", "productive_morphology",
    "current_component_semantics", "genealogy_stage",
)

CODEBOOK_FIELDS = (
    "lexical_id", "semantic_entity_id", "semantic_category",
    "historical_stem_id", "canonical_hidden_form", "final_realization_rules",
    "irregularity_flags",
)

GENEALOGY_FIELDS = (
    "stage", "rule_id", "process_type", "input_ids", "output_ids",
    "conditioning", "currently_productive", "notes",
)

SEPARATORS = {"PAGE", "PARAGRAPH", "RECORD", "LINE", "FIELD", "SPACE", "JOIN", "NONE"}
REQUIRED_META = {
    "world_id", "title", "broad_family", "practical_domain",
    "semantics_light", "organic_evolution", "clean_engineered_control",
    "adversarial_pair_id", "carrier_profile", "alphabet", "registers",
    "hands", "evolution_processes", "generator_schema",
}


def seeded_rng(world_id: str, seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:{world_id}:{seed}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def stable_id(prefix: str, *parts: object, width: int = 12) -> str:
    raw = "\x1f".join(map(str, parts)).encode()
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:width]}"


def validate_rows(meta: dict, bundle: dict, target_events: int) -> None:
    missing = REQUIRED_META - set(meta)
    if missing:
        raise ValueError(f"WORLD_META missing {sorted(missing)}")
    if meta["generator_schema"] != "GDT395_WORLD_GENERATOR_V1":
        raise ValueError("wrong generator_schema")
    if set(bundle) != {"observations", "oracle", "codebook", "genealogy"}:
        raise ValueError("bundle keys must be observations/oracle/codebook/genealogy")
    obs, oracle = bundle["observations"], bundle["oracle"]
    if len(obs) != len(oracle) or len(obs) < target_events:
        raise ValueError("event count/oracle mismatch or target not reached")
    if len(obs) > target_events + 64:
        raise ValueError("generator exceeded target by more than one bounded record")
    ids = set()
    for row in obs:
        if set(row) != set(OBS_FIELDS):
            raise ValueError(f"bad observation fields: {set(row) ^ set(OBS_FIELDS)}")
        if row["event_id"] in ids:
            raise ValueError("duplicate event_id")
        ids.add(row["event_id"])
        if row["separator_before"] not in SEPARATORS or row["separator_after"] not in SEPARATORS:
            raise ValueError("bad separator")
    for row in oracle:
        if set(row) != set(ORACLE_FIELDS):
            raise ValueError(f"bad oracle fields: {set(row) ^ set(ORACLE_FIELDS)}")
        if row["event_id"] not in ids:
            raise ValueError("oracle event absent from observation")
    if {r["event_id"] for r in oracle} != ids:
        raise ValueError("oracle/observation key mismatch")
    for row in bundle["codebook"]:
        if set(row) != set(CODEBOOK_FIELDS):
            raise ValueError("bad codebook fields")
    for row in bundle["genealogy"]:
        if set(row) != set(GENEALOGY_FIELDS):
            raise ValueError("bad genealogy fields")


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def pipe(values: Iterable[object]) -> str:
    vals = sorted({str(v) for v in values if str(v) and str(v) != "NONE"})
    return "|".join(vals) if vals else "NONE"
