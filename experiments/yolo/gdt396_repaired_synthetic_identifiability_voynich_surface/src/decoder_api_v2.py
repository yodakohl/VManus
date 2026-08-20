#!/usr/bin/env python3
"""Generic oracle-blind GDT396 decoder output schema V2."""

from __future__ import annotations

import math
import re


API_VERSION = 2
SAFE_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
PHASES = ("DEVELOPMENT", "QUALIFICATION", "CONFIRMATION")
SURFACES = ("FREE_SURFACE", "VOYNICH_SURFACE")
METHOD_VARIANTS = ("PRIMARY", "MULTI_CONSTRAINT", "SCALAR_BOTTLENECK")
CLAIM_STATUSES = ("RESOLVED", "ABSTAIN", "UNSUPPORTED")
REPRESENTATIONS = (
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY", "MULTI_RESOLUTION",
)
PARTITION_PROPERTIES = (
    "LEXICAL_IDENTITY", "SEMANTIC_ENTITY_IDENTITY", "HISTORICAL_ANCESTRY",
    "CURRENT_PRODUCTIVE_COMPONENT", "FOSSIL_COMPONENT", "CURRENT_SHARED_MEANING",
    "FUNCTION_OPERATOR_CLASS", "CONSTRUCTION_CLASS", "REGISTER_REALIZATION",
    "SEMANTIC_CATEGORY", "STATE_BEFORE_IDENTITY", "STATE_AFTER_IDENTITY",
    "STATE_TRANSITION_IDENTITY",
)
BINARY_PROPERTIES = (
    "PRODUCTIVE_MORPHOLOGY", "FOSSILIZED_MORPHOLOGY",
    "TEMPORAL_STATE_GATE", "ENTITY_REUSE_PRESENT",
)
TARGET_PROPERTIES = (
    "GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION",
    "REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT",
)
MORPHOLOGY_STATUSES = ("CURRENTLY_PRODUCTIVE", "FOSSILIZED", "NO_COMPONENT_CLAIM")
ARCHITECTURE_BINARY_PROPERTIES = (
    "LANGUAGE_LIKE", "NOTATION_LIKE", "CODEBOOK_LIKE", "ORGANIC_EVOLUTION_LIKE",
    "CLEAN_ENGINEERED_LIKE", "SEMANTICS_LIGHT_LIKE",
)
COMMON = (
    "schema_version", "phase", "run_id", "world_id", "corpus_seed", "surface_id",
    "representation_id", "decoder_id", "method_variant", "property_id",
)
TABLE_FIELDS = {
    "partition_claims": COMMON + (
        "unit_type", "unit_id", "claim_status", "cluster_id", "confidence",
    ),
    "binary_claims": COMMON + (
        "unit_type", "unit_id", "claim_status", "predicted_bool", "confidence",
    ),
    "target_queries": COMMON + (
        "source_event_id", "candidate_set_id", "claim_status",
        "predicted_target_count", "confidence",
    ),
    "target_ranks": COMMON + (
        "source_event_id", "candidate_set_id", "target_rank", "target_event_id",
        "target_score", "type_id",
    ),
    "scope_claims": COMMON + (
        "source_event_id", "claim_status", "scope_present", "predicted_start_event_id",
        "predicted_end_event_id", "scope_type_id", "confidence",
    ),
    "morphology_claims": COMMON + (
        "event_id", "component_id", "start_offset", "end_offset", "morphology_status",
        "claim_status", "rank", "confidence",
    ),
    "record_partition_claims": COMMON + (
        "record_id", "claim_status", "record_schema_cluster_id", "confidence",
    ),
    "architecture_partition_claims": COMMON + (
        "claim_status", "architecture_cluster_id", "confidence",
    ),
    "architecture_binary_claims": COMMON + (
        "claim_status", "predicted_bool", "confidence",
    ),
}


def unresolved_outputs() -> dict[str, list[dict]]:
    return {name: [] for name in TABLE_FIELDS}


def _probability(row: dict, key: str, table: str) -> None:
    value = float(row[key])
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{table}: {key} outside [0,1]")


def validate_shape(outputs: dict[str, list[dict]]) -> None:
    if set(outputs) != set(TABLE_FIELDS):
        raise ValueError(f"output table mismatch: {set(outputs) ^ set(TABLE_FIELDS)}")
    for table, rows in outputs.items():
        if not isinstance(rows, list):
            raise TypeError(f"{table}: rows must be a list")
        expected = set(TABLE_FIELDS[table])
        for row in rows:
            if set(row) != expected:
                raise ValueError(f"{table}: bad fields {set(row) ^ expected}")
            if int(row["schema_version"]) != API_VERSION:
                raise ValueError(f"{table}: wrong schema version")
            if row["phase"] not in PHASES or row["surface_id"] not in SURFACES:
                raise ValueError(f"{table}: bad phase/surface")
            if row["method_variant"] not in METHOD_VARIANTS:
                raise ValueError(f"{table}: bad method variant")
            if row["representation_id"] not in REPRESENTATIONS:
                raise ValueError(f"{table}: unknown representation")
            for key in ("run_id", "world_id", "decoder_id"):
                if not SAFE_ID.fullmatch(str(row[key])):
                    raise ValueError(f"{table}: unsafe {key}")
            if "claim_status" in row and row["claim_status"] not in CLAIM_STATUSES:
                raise ValueError(f"{table}: bad claim status")
            if "confidence" in row:
                _probability(row, "confidence", table)
            if "target_score" in row:
                _probability(row, "target_score", table)
            if table in ("binary_claims", "architecture_binary_claims") and type(row["predicted_bool"]) is not bool:
                raise ValueError(f"{table}: predicted_bool must be a Python bool before serialization")
            if table == "scope_claims" and type(row["scope_present"]) is not bool:
                raise ValueError("scope_claims: scope_present must be a Python bool before serialization")
            prop = row["property_id"]
            if table == "partition_claims" and prop not in PARTITION_PROPERTIES:
                raise ValueError("unknown partition property")
            if table == "binary_claims" and prop not in BINARY_PROPERTIES:
                raise ValueError("unknown binary property")
            if table in ("target_queries", "target_ranks") and prop not in TARGET_PROPERTIES:
                raise ValueError("unknown target property")
            if table == "scope_claims" and prop != "SCOPE":
                raise ValueError("scope property must be SCOPE")
            if table == "morphology_claims":
                if prop != "MORPHOLOGY_ANALYSIS" or row["morphology_status"] not in MORPHOLOGY_STATUSES:
                    raise ValueError("bad morphology claim")
            if table == "record_partition_claims" and prop != "RECORD_SCHEMA":
                raise ValueError("record property must be RECORD_SCHEMA")
            if table == "architecture_partition_claims" and prop != "WORLD_ARCHITECTURE":
                raise ValueError("bad architecture partition property")
            if table == "architecture_binary_claims" and prop not in ARCHITECTURE_BINARY_PROPERTIES:
                raise ValueError("bad architecture binary property")
