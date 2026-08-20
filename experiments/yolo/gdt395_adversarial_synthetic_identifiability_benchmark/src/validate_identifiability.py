#!/usr/bin/env python3
"""Independent, non-importing validator for GDT395 identifiability scoring.

This module intentionally duplicates the frozen public schemas and metric
formulae.  It never imports a decoder, generator, scorer, or project helper.
Claims are authenticated and structurally validated before any oracle file is
opened.  Errors expose gate codes only, never paths, event IDs, or oracle
values.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[4]
EXPERIMENT_REL = Path(
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
)

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

ORACLE_FIELDS = (
    "world_id", "corpus_seed", "event_id", "domain_id", "activity_id",
    "lexical_id", "semantic_entity_id", "semantic_category", "function_class",
    "relation_type", "relation_target_event_id", "state_before", "state_after",
    "historical_stem_id", "current_morpheme_ids", "fossilized_component_ids",
    "construction_id", "scope_start_event_id", "scope_end_event_id",
    "record_schema_id", "register_realization_id", "productive_morphology",
    "current_component_semantics", "genealogy_stage",
)

CORPUS_MANIFEST_FIELDS = (
    "world_id", "corpus_seed", "events", "record_rewriter",
    "observation_relpath", "observation_sha256", "oracle_relpath",
    "oracle_sha256",
)

REPRESENTATIONS = (
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
)
WORLDS = tuple(f"W{i:02d}" for i in range(1, 11))
MEANINGFUL_WORLDS = WORLDS[:9]
PAIR_WORLDS = ("W02", "W03", "W09", "W10")
HELD_SEEDS = tuple(range(15, 20))
UNRESOLVED = "UNRESOLVED"
NA = "NA"

ALL_PROPERTIES = (
    "LEXICAL_IDENTITY", "SEMANTIC_ENTITY_IDENTITY",
    "HISTORICAL_STEM_ANCESTRY", "PRODUCTIVE_MORPHOLOGY",
    "FOSSILIZED_MORPHOLOGY", "FUNCTION_CLASS", "COORDINATOR_RELATION",
    "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA", "TEMPORAL_STATE_GATE",
    "SCOPE", "ENTITY_REUSE", "OPERATOR_CLASS", "RECORD_SCHEMA",
    "REGISTER_LOCAL_VARIANT", "SEMANTIC_CATEGORY", "ACTUAL_LEXICAL_MEANING",
)

SCOREABLE = {
    "LEXICAL_IDENTITY": ("lexical_cluster", "lexical_id"),
    "SEMANTIC_ENTITY_IDENTITY": ("entity_cluster", "semantic_entity_id"),
    "HISTORICAL_STEM_ANCESTRY": ("stem_cluster", "historical_stem_id"),
    "FUNCTION_CLASS": ("function_cluster", "function_class"),
    "ENTITY_REUSE": ("entity_cluster", "semantic_entity_id"),
    "REGISTER_LOCAL_VARIANT": ("register_variant_cluster", "register_realization_id"),
    "SEMANTIC_CATEGORY": ("semantic_category_cluster", "semantic_category"),
}

HOLD_PROPERTIES = tuple(p for p in ALL_PROPERTIES if p not in SCOREABLE)

QUALIFICATIONS = {
    "LEXICAL_IDENTITY": "ANONYMOUS_LEXICAL_ID_PARTITION_NOT_WORD_MEANING",
    "SEMANTIC_ENTITY_IDENTITY": "ANONYMOUS_ENTITY_COIDENTITY_ONLY",
    "HISTORICAL_STEM_ANCESTRY": "SHARED_HISTORICAL_STEM_PARTITION_NOT_GENEALOGY",
    "PRODUCTIVE_MORPHOLOGY": "UNSCORED_INTERFACE_HOLD_OPAQUE_COMPONENT_ID_NOT_BOOLEAN",
    "FOSSILIZED_MORPHOLOGY": "UNSCORED_INTERFACE_HOLD_OPAQUE_COMPONENT_ID_NOT_BOOLEAN",
    "FUNCTION_CLASS": "ANONYMOUS_FUNCTION_CLASS_PARTITION_ONLY",
    "COORDINATOR_RELATION": "UNSCORED_INTERFACE_HOLD_NO_TYPED_RANKED_TARGET_MAPPING",
    "ALTERNATIVE_RELATION": "UNSCORED_INTERFACE_HOLD_NO_TYPED_RANKED_TARGET_MAPPING",
    "REFERENCE_ANAPHORA": "UNSCORED_INTERFACE_HOLD_NO_DIRECT_ORACLE_REFERENCE_TARGET",
    "TEMPORAL_STATE_GATE": "UNSCORED_INTERFACE_HOLD_NO_MATCHING_CLAIM_TRUTH_FIELD",
    "SCOPE": "UNSCORED_INTERFACE_HOLD_NO_VALIDATED_EVENT_ORDER_CONTRACT",
    "ENTITY_REUSE": "RECURRING_ANONYMOUS_ENTITY_IDS_ONLY_SINGLETON_TRUTH_INELIGIBLE",
    "OPERATOR_CLASS": "UNSCORED_INTERFACE_HOLD_NO_ORACLE_OPERATOR_CLASS",
    "RECORD_SCHEMA": "UNSCORED_INTERFACE_HOLD_NO_RECORD_ID_IN_ACCEPTED_INPUT",
    "REGISTER_LOCAL_VARIANT": "AUTHENTIC_REGISTER_REALIZATION_IDENTITY_NOT_MEANING",
    "SEMANTIC_CATEGORY": "ANONYMOUS_CATEGORY_PARTITION_NOT_CATEGORY_MEANING",
    "ACTUAL_LEXICAL_MEANING": "UNSCORED_INTERFACE_HOLD_REQUIRES_EXTERNAL_GROUNDING",
}

CLUSTER_COMPONENT_FIELDS = (
    "entity_cluster", "lexical_cluster", "stem_cluster", "function_cluster",
    "operator_cluster", "construction_cluster", "register_variant_cluster",
    "semantic_category_cluster", "productive_component_prediction",
    "fossilized_component_prediction", "record_schema_cluster",
)
TARGET_FIELDS = (
    "predicted_relation_target_event_id", "predicted_reference_target_event_id",
    "predicted_scope_start_event_id", "predicted_scope_end_event_id",
)
TRUTH_CLUSTER_FIELDS = tuple(sorted({truth for _, truth in SCOREABLE.values()}))

PANEL_FIELDS = (
    "view", "world_id", "corpus_seed", "representation", "decoder_id",
    "property", "kind", "status", "eligible_n", "prediction_n", "coverage",
    "nmi", "ari", "pair_f1", "balanced_accuracy", "mcc", "fdr", "top1",
    "mrr", "mrr_above_chance", "endpoint_accuracy", "exact_scope_accuracy",
    "interval_iou", "target_distance_mae", "false_discoveries",
    "absent_truth_n", "unresolved_n", "invalid_n", "co_cluster_fpr",
    "false_positive_rate", "primary_index", "threshold_pass",
    "endpoint_qualification", "metric_note",
)

WORLD_REP_FIELDS = (
    "view", "property", "world_id", "representation", "status",
    "decoders_scored", "decoders_clear", "luna_decoders_clear",
    "median_decoder_clear", "endpoint_qualification", "coverage", "nmi",
    "ari", "pair_f1", "balanced_accuracy", "mcc", "fdr", "top1", "mrr",
    "mrr_above_chance", "endpoint_accuracy", "exact_scope_accuracy",
    "interval_iou", "target_distance_mae", "primary_index",
    "false_positive_rate", "co_cluster_fpr",
)

DECISION_FIELDS = (
    "property", "decision", "endpoint_qualification", "exploratory_pattern",
    "representation", "worlds_clear", "meaningful_worlds_clear",
    "clear_world_ids", "clear_world_families", "w10_false_positive_rate",
    "w10_false_positive_upper95", "w10_guard_pass",
    "organic_confusion_flag", "organic_confusion_representations",
    "raw_p_value", "holm_adjusted_p_value", "inference_status",
)

W10_FIELDS = (
    "property", "representation", "endpoint_qualification", "panels",
    "seed_false_positive_rates", "false_positive_rate",
    "false_positive_upper95", "upper95_method", "point_guard_pass",
    "confirmatory_guard_pass", "inference_status",
)

ARCH_FIELDS = (
    "decoder_id", "endpoint", "truth_basis", "n", "nmi", "ari",
    "pair_f1", "balanced_accuracy", "mcc", "fdr",
)

STRESS_FIELDS = ("stress_test", "status")
STRESS_TESTS = (
    "EXACT_COMPOSITE_AS_WORD",
    "UNIVERSAL_VS_WORLD_LOCAL_COEFFICIENTS",
    "FREQUENCY_POSITION_RECURRENCE_RESIDUALIZATION",
    "SCALAR_ROLE_BOTTLENECKS",
    "FIXED_SHORT_HORIZON_OUTCOMES",
    "MULTI_CONSTRAINT_INTERSECTION_REPLACEMENT",
)

OUTPUT_FILES = (
    "panel_metrics.tsv", "pair_panel_metrics.tsv",
    "world_representation_metrics.tsv", "property_decisions.tsv",
    "w10_false_discoveries.tsv", "architecture_metrics.tsv",
    "method_stress_tests.tsv", "summary.json",
)

SUMMARY_KEYS = {
    "schema", "status", "panel", "input_sha256", "decisions",
    "endpoint_qualification", "interface_hold_properties",
    "confirmatory_promotions_enabled", "unscored_method_stress_tests",
    "ambiguities", "contains_event_rows", "voynich_rows",
}

SAFE_WORLD = re.compile(r"^W(?:0[1-9]|10)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
WORLD_TOKEN_RE = re.compile(r"(?<![A-Z0-9])W(?:0[1-9]|10)(?![A-Z0-9])")


class ValidationError(Exception):
    """A sanitized validation failure carrying only a stable gate code."""


def fail(code: str) -> None:
    raise ValidationError(code)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
    except OSError:
        fail("FILE_ACCESS_GATE")
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii")


def read_json(path: Path, code: str) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError):
        fail(code)


def validate_content_hash(data: Any, code: str) -> None:
    if not isinstance(data, dict) or not isinstance(data.get("content_sha256"), str):
        fail(code)
    expected = data["content_sha256"]
    if not SHA256_RE.fullmatch(expected):
        fail(code)
    body = dict(data)
    body.pop("content_sha256")
    actual = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    if actual != expected:
        fail(code)


def validate_checks(data: dict, code: str) -> None:
    checks = data.get("checks")
    if not isinstance(checks, dict) or not checks:
        fail(code)
    if any(type(value) is not bool or not value for value in checks.values()):
        fail(code)


def portable_label(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=True).relative_to(root.resolve(strict=True)).as_posix()
    except (OSError, ValueError):
        fail("PORTABLE_PATH_GATE")


def bound_path(root: Path, label: str) -> Path:
    if not isinstance(label, str) or not label or "\\" in label:
        fail("BOUND_PATH_GATE")
    relative = Path(label)
    if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
        fail("BOUND_PATH_GATE")
    try:
        root_resolved = root.resolve(strict=True)
        path = (root_resolved / relative).resolve(strict=True)
        path.relative_to(root_resolved)
    except (OSError, ValueError):
        fail("BOUND_PATH_GATE")
    if not path.is_file() or path.is_symlink():
        fail("BOUND_PATH_GATE")
    return path


def validate_binding(binding: Any, code: str) -> tuple[str, str]:
    if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
        fail(code)
    label, digest = binding["path"], binding["sha256"]
    if not isinstance(label, str) or not isinstance(digest, str):
        fail(code)
    if not SHA256_RE.fullmatch(digest):
        fail(code)
    return label, digest


def freeze_claim_bindings(data: dict) -> dict[str, list[tuple[str, str]]]:
    bindings = data.get("bindings")
    roles = {"authentic_event_claims", "pair_event_claims", "world_claims"}
    if not isinstance(bindings, dict) or set(bindings) != roles | {"implementation"}:
        fail("CLAIM_BINDING_ROLE_GATE")
    answer: dict[str, list[tuple[str, str]]] = {}
    seen: set[str] = set()
    for role in sorted(roles):
        values = bindings[role]
        if not isinstance(values, list) or not values:
            fail("CLAIM_BINDING_ROLE_GATE")
        normalized = [validate_binding(value, "CLAIM_BINDING_SHAPE_GATE") for value in values]
        labels = [label for label, _ in normalized]
        if len(labels) != len(set(labels)) or any(label in seen for label in labels):
            fail("CLAIM_BINDING_DISJOINT_GATE")
        seen.update(labels)
        answer[role] = normalized
    return answer


def validation_freeze_binding(data: dict) -> tuple[str, str]:
    bindings = data.get("bindings")
    candidates: list[Any] = []
    if isinstance(bindings, dict):
        value = bindings.get("claims_freeze")
        if isinstance(value, list):
            candidates.extend(value)
        elif value is not None:
            candidates.append(value)
    elif isinstance(bindings, list):
        for value in bindings:
            if isinstance(value, dict) and value.get("role") == "claims_freeze":
                if set(value) != {"role", "path", "sha256"}:
                    fail("VALIDATION_FREEZE_BINDING_GATE")
                candidates.append({"path": value["path"], "sha256": value["sha256"]})
    if len(candidates) != 1:
        fail("VALIDATION_FREEZE_BINDING_GATE")
    return validate_binding(candidates[0], "VALIDATION_FREEZE_BINDING_GATE")


def implementation_entries(data: dict) -> dict[str, dict]:
    raw = data.get("implementation_map")
    entries: list[dict]
    if isinstance(raw, dict):
        entries = []
        for key, value in raw.items():
            if not isinstance(value, dict):
                fail("IMPLEMENTATION_MAP_GATE")
            item = dict(value)
            if item.get("decoder_id", key) != key:
                fail("IMPLEMENTATION_MAP_GATE")
            item["decoder_id"] = key
            entries.append(item)
    elif isinstance(raw, list):
        entries = raw
    else:
        fail("IMPLEMENTATION_MAP_GATE")
    if len(entries) != 5:
        fail("IMPLEMENTATION_MAP_GATE")
    result: dict[str, dict] = {}
    for item in entries:
        if not isinstance(item, dict):
            fail("IMPLEMENTATION_MAP_GATE")
        decoder = item.get("decoder_id")
        family = item.get("model_family")
        if not isinstance(decoder, str) or not decoder or decoder in result:
            fail("IMPLEMENTATION_MAP_GATE")
        if item.get("oracle_blind") is not True or family not in {"SOL", "LUNA"}:
            fail("IMPLEMENTATION_MAP_GATE")
        result[decoder] = item
    families = Counter(item["model_family"] for item in result.values())
    if families != Counter({"SOL": 2, "LUNA": 3}):
        fail("IMPLEMENTATION_MODEL_MIX_GATE")
    return result


def iter_implementation_bindings(value: Any) -> Iterable[tuple[str, str]]:
    """Yield path/hash pairs from common implementation-binding containers."""
    if isinstance(value, dict):
        if {"path", "sha256"}.issubset(value):
            label, digest = value["path"], value["sha256"]
            if not isinstance(label, str) or not isinstance(digest, str):
                fail("IMPLEMENTATION_BINDING_GATE")
            if not SHA256_RE.fullmatch(digest):
                fail("IMPLEMENTATION_BINDING_GATE")
            yield label, digest
            return
        for key, child in value.items():
            if isinstance(child, str) and SHA256_RE.fullmatch(child) and isinstance(key, str):
                yield key, child
            else:
                yield from iter_implementation_bindings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_implementation_bindings(child)


def require_implementation_binding(
    freeze: dict, root: Path, path: Path, code: str,
) -> None:
    try:
        experiment = (root / EXPERIMENT_REL).resolve(strict=True)
        label = path.resolve(strict=True).relative_to(experiment).as_posix()
    except (OSError, ValueError):
        fail(code)
    digest = sha256_file(path)
    bindings = freeze.get("bindings")
    if not isinstance(bindings, dict) or "implementation" not in bindings:
        fail(code)
    matches = [pair for pair in iter_implementation_bindings(bindings["implementation"])
               if pair[0] == label]
    if len(matches) != 1 or matches[0][1] != digest:
        fail(code)


def open_tsv(path: Path):
    try:
        if path.suffix == ".gz":
            return gzip.open(path, "rt", encoding="utf-8", newline="")
        return path.open("r", encoding="utf-8", newline="")
    except OSError:
        fail("TSV_OPEN_GATE")


def parse_seed(value: Any, code: str) -> int:
    if isinstance(value, bool):
        fail(code)
    text = str(value)
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)", text):
        fail(code)
    return int(text)


def parse_finite(value: Any, code: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        fail(code)
    if not math.isfinite(result):
        fail(code)
    return result


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def fmt_float(value: float | None) -> str:
    if value is None:
        return NA
    if value == 0:
        value = 0.0
    return format(value, ".12g")


def median_or_none(values: Iterable[float | None]) -> float | None:
    finite = [value for value in values if value is not None]
    return float(statistics.median(finite)) if finite else None


@dataclass(frozen=True)
class ClaimInfo:
    path: Path
    label: str
    world_id: str
    seed: int
    representation: str
    decoder_id: str
    event_ids: frozenset[str]


@dataclass(frozen=True)
class WorldClaim:
    world_id: str
    decoder_id: str
    claim: dict[str, Any]


def validate_opaque(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value or any(ord(ch) < 32 for ch in value):
        fail(code)
    if value in {"NONE", "NONCOMPARABLE"}:
        fail(code)
    return value


def validate_event_id(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value or "|" in value or any(ch.isspace() for ch in value):
        fail(code)
    return value


def validate_event_claim_file(
    path: Path, label: str, decoders: set[str], expected_worlds: set[str],
) -> ClaimInfo:
    try:
        handle = open_tsv(path)
        with handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != CLAIM_FIELDS:
                fail("CLAIM_SCHEMA_GATE")
            combo: tuple[str, int, str, str] | None = None
            ids: set[str] = set()
            targets: list[tuple[str, ...]] = []
            for row in reader:
                if set(row) != set(CLAIM_FIELDS):
                    fail("CLAIM_SCHEMA_GATE")
                world = row["world_id"]
                seed = parse_seed(row["corpus_seed"], "CLAIM_SEED_GATE")
                representation = row["representation"]
                decoder = row["decoder_id"]
                current = (world, seed, representation, decoder)
                if combo is None:
                    combo = current
                elif current != combo:
                    fail("CLAIM_FILE_PROVENANCE_GATE")
                if world not in expected_worlds or seed not in HELD_SEEDS:
                    fail("CLAIM_FILE_PROVENANCE_GATE")
                if representation not in REPRESENTATIONS or decoder not in decoders:
                    fail("CLAIM_FILE_PROVENANCE_GATE")
                event_id = validate_event_id(row["event_id"], "CLAIM_EVENT_ID_GATE")
                if event_id in ids:
                    fail("CLAIM_DUPLICATE_EVENT_GATE")
                ids.add(event_id)
                confidence = parse_finite(row["confidence"], "CLAIM_CONFIDENCE_GATE")
                if confidence < 0 or confidence > 1:
                    fail("CLAIM_CONFIDENCE_GATE")
                for field in CLUSTER_COMPONENT_FIELDS:
                    validate_opaque(row[field], "CLAIM_OPAQUE_FIELD_GATE")
                target_values = []
                for field in TARGET_FIELDS:
                    value = row[field]
                    if value != UNRESOLVED:
                        validate_event_id(value, "CLAIM_TARGET_SHAPE_GATE")
                    target_values.append(value)
                targets.append(tuple(target_values))
    except (csv.Error, UnicodeError, EOFError):
        fail("CLAIM_TSV_PARSE_GATE")
    if combo is None or not ids:
        fail("CLAIM_EMPTY_FILE_GATE")
    for values in targets:
        if any(value != UNRESOLVED and value not in ids for value in values):
            fail("CLAIM_TARGET_MEMBERSHIP_GATE")
    return ClaimInfo(path, label, combo[0], combo[1], combo[2], combo[3], frozenset(ids))


def world_from_label(label: str) -> str:
    tokens = WORLD_TOKEN_RE.findall(label)
    if len(tokens) != 1:
        fail("WORLD_CLAIM_PATH_TOKEN_GATE")
    return tokens[0]


def validate_world_hypothesis(value: Any) -> None:
    if value == UNRESOLVED:
        return
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = parse_finite(value, "WORLD_CLAIM_HYPOTHESIS_GATE")
        if 0 <= number <= 1:
            return
    if isinstance(value, str) and value.upper() in {"HIGH", "MEDIUM", "LOW", "TRUE", "FALSE"}:
        return
    fail("WORLD_CLAIM_HYPOTHESIS_GATE")


def validate_world_claim(path: Path, label: str, decoders: set[str]) -> WorldClaim:
    data = read_json(path, "WORLD_CLAIM_JSON_GATE")
    path_world = world_from_label(label)
    if not isinstance(data, dict):
        fail("WORLD_CLAIM_SCHEMA_GATE")
    if set(data) == set(WORLD_CLAIM_FIELDS):
        world, claim = path_world, data
    elif set(data) == set(WORLD_CLAIM_FIELDS) | {"world_id"}:
        world = data["world_id"]
        claim = {key: data[key] for key in WORLD_CLAIM_FIELDS}
    elif set(data) in ({"world_id", "claim"}, {"world_id", "world_claim"}):
        world = data["world_id"]
        key = "claim" if "claim" in data else "world_claim"
        claim = data[key]
        if not isinstance(claim, dict) or set(claim) != set(WORLD_CLAIM_FIELDS):
            fail("WORLD_CLAIM_SCHEMA_GATE")
    else:
        fail("WORLD_CLAIM_SCHEMA_GATE")
    if world != path_world or world not in WORLDS:
        fail("WORLD_CLAIM_WORLD_GATE")
    decoder = claim.get("decoder_id")
    if decoder not in decoders:
        fail("WORLD_CLAIM_DECODER_GATE")
    validate_opaque(claim.get("architecture_cluster"), "WORLD_CLAIM_CLUSTER_GATE")
    for field in ("language_like", "notation_like", "codebook_like", "semantics_light_like"):
        validate_world_hypothesis(claim.get(field))
    confidence = parse_finite(claim.get("confidence"), "WORLD_CLAIM_CONFIDENCE_GATE")
    if not 0 <= confidence <= 1:
        fail("WORLD_CLAIM_CONFIDENCE_GATE")
    return WorldClaim(world, decoder, claim)


def authenticate_and_validate_claims(
    root: Path, bindings: dict[str, list[tuple[str, str]]], decoders: set[str],
) -> tuple[list[ClaimInfo], list[ClaimInfo], dict[tuple[str, str], WorldClaim]]:
    expected_counts = {
        "authentic_event_claims": len(WORLDS) * len(HELD_SEEDS) * len(REPRESENTATIONS) * 5,
        "pair_event_claims": len(PAIR_WORLDS) * len(HELD_SEEDS) * len(REPRESENTATIONS) * 5,
        "world_claims": len(WORLDS) * 5,
    }
    resolved: dict[str, list[tuple[Path, str]]] = {}
    for role, values in bindings.items():
        if len(values) != expected_counts[role]:
            fail("CLAIM_BOUND_FILE_COUNT_GATE")
        resolved[role] = []
        for label, digest in values:
            path = bound_path(root, label)
            if sha256_file(path) != digest:
                fail("CLAIM_BOUND_HASH_GATE")
            resolved[role].append((path, label))

    authentic = [
        validate_event_claim_file(path, label, decoders, set(WORLDS))
        for path, label in resolved["authentic_event_claims"]
    ]
    pairs = [
        validate_event_claim_file(path, label, decoders, set(PAIR_WORLDS))
        for path, label in resolved["pair_event_claims"]
    ]
    auth_combos = {(x.world_id, x.seed, x.representation, x.decoder_id) for x in authentic}
    pair_combos = {(x.world_id, x.seed, x.representation, x.decoder_id) for x in pairs}
    expected_auth = set(itertools.product(WORLDS, HELD_SEEDS, REPRESENTATIONS, sorted(decoders)))
    expected_pair = set(itertools.product(PAIR_WORLDS, HELD_SEEDS, REPRESENTATIONS, sorted(decoders)))
    if len(auth_combos) != len(authentic) or auth_combos != expected_auth:
        fail("AUTHENTIC_PANEL_COMPLETENESS_GATE")
    if len(pair_combos) != len(pairs) or pair_combos != expected_pair:
        fail("PAIR_PANEL_COMPLETENESS_GATE")

    auth_events: dict[tuple[str, int], frozenset[str]] = {}
    for info in authentic:
        key = (info.world_id, info.seed)
        prior = auth_events.setdefault(key, info.event_ids)
        if prior != info.event_ids:
            fail("AUTHENTIC_EVENT_RECURRENCE_GATE")
    pair_events: dict[tuple[str, int], frozenset[str]] = {}
    for info in pairs:
        key = (info.world_id, info.seed)
        prior = pair_events.setdefault(key, info.event_ids)
        if prior != info.event_ids:
            fail("PAIR_EVENT_RECURRENCE_GATE")
    for key, event_ids in pair_events.items():
        if not event_ids.issubset(auth_events[key]):
            fail("PAIR_EVENT_SUBSET_GATE")

    world_claims: dict[tuple[str, str], WorldClaim] = {}
    for path, label in resolved["world_claims"]:
        item = validate_world_claim(path, label, decoders)
        key = (item.world_id, item.decoder_id)
        if key in world_claims:
            fail("WORLD_CLAIM_DUPLICATE_GATE")
        world_claims[key] = item
    if set(world_claims) != set(itertools.product(WORLDS, sorted(decoders))):
        fail("WORLD_CLAIM_COMPLETENESS_GATE")
    return authentic, pairs, world_claims


@dataclass(frozen=True)
class OracleBundle:
    truths: dict[tuple[str, int], dict[str, dict[str, str]]]
    event_sets: dict[tuple[str, int], frozenset[str]]
    labels_and_hashes: tuple[tuple[str, str], ...]


def valid_pipe_value(value: str, code: str) -> tuple[str, ...]:
    if not isinstance(value, str) or not value or value == UNRESOLVED:
        fail(code)
    atoms = value.split("|")
    if any(not atom or atom != atom.strip() or any(ch.isspace() for ch in atom) for atom in atoms):
        fail(code)
    if len(atoms) != len(set(atoms)) or atoms != sorted(atoms):
        fail(code)
    if "NONE" in atoms and len(atoms) != 1:
        fail(code)
    return tuple(atoms)


def read_corpus_manifest(path: Path) -> dict[tuple[str, int], dict[str, str]]:
    rows: dict[tuple[str, int], dict[str, str]] = {}
    try:
        handle = open_tsv(path)
        with handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != CORPUS_MANIFEST_FIELDS:
                fail("CORPUS_MANIFEST_SCHEMA_GATE")
            for row in reader:
                if set(row) != set(CORPUS_MANIFEST_FIELDS):
                    fail("CORPUS_MANIFEST_SCHEMA_GATE")
                world = row["world_id"]
                seed = parse_seed(row["corpus_seed"], "CORPUS_MANIFEST_SEED_GATE")
                if world not in WORLDS or seed not in range(20):
                    fail("CORPUS_MANIFEST_PANEL_GATE")
                events = parse_seed(row["events"], "CORPUS_MANIFEST_EVENT_COUNT_GATE")
                if not 8448 <= events <= 8512:
                    fail("CORPUS_MANIFEST_EVENT_COUNT_GATE")
                if not SHA256_RE.fullmatch(row["observation_sha256"] or ""):
                    fail("CORPUS_MANIFEST_HASH_GATE")
                if not SHA256_RE.fullmatch(row["oracle_sha256"] or ""):
                    fail("CORPUS_MANIFEST_HASH_GATE")
                expected_oracle = f"sealed/{world}/seed_{seed:02d}_oracle.tsv.gz"
                if row["oracle_relpath"] != expected_oracle:
                    fail("CORPUS_MANIFEST_ORACLE_PATH_GATE")
                key = (world, seed)
                if key in rows:
                    fail("CORPUS_MANIFEST_DUPLICATE_GATE")
                rows[key] = row
    except (csv.Error, UnicodeError, EOFError):
        fail("CORPUS_MANIFEST_PARSE_GATE")
    if set(rows) != set(itertools.product(WORLDS, range(20))):
        fail("CORPUS_MANIFEST_COMPLETENESS_GATE")
    return rows


def validate_oracle_scalar_fields(row: dict[str, str]) -> None:
    for field in ORACLE_FIELDS:
        value = row[field]
        if value is None or value == "" or value == UNRESOLVED:
            fail("ORACLE_VALUE_GATE")
        if field not in {"corpus_seed", "productive_morphology"}:
            valid_pipe_value(value, "ORACLE_PIPE_GATE")
    if row["productive_morphology"] not in {"True", "False", "true", "false"}:
        fail("ORACLE_BOOLEAN_GATE")
    for field in TRUTH_CLUSTER_FIELDS:
        atoms = valid_pipe_value(row[field], "ORACLE_CLUSTER_TRUTH_GATE")
        if atoms != ("NONE",) and len(atoms) != 1:
            fail("ORACLE_CLUSTER_TRUTH_GATE")


def authenticate_and_read_oracles(
    oracle_root: Path, manifest_path: Path, manifest: dict[tuple[str, int], dict[str, str]],
    authentic_events: dict[tuple[str, int], frozenset[str]],
    pair_events: dict[tuple[str, int], frozenset[str]],
) -> OracleBundle:
    held_rows = {key: row for key, row in manifest.items() if key[1] in HELD_SEEDS}
    if set(held_rows) != set(itertools.product(WORLDS, HELD_SEEDS)):
        fail("HELD_ORACLE_MANIFEST_GATE")

    paths: dict[tuple[str, int], tuple[Path, str, str]] = {}
    for key, row in held_rows.items():
        label = row["oracle_relpath"]
        path = bound_path(oracle_root, label)
        digest = row["oracle_sha256"]
        if sha256_file(path) != digest:
            fail("HELD_ORACLE_HASH_GATE")
        paths[key] = (path, label, digest)

    truths: dict[tuple[str, int], dict[str, dict[str, str]]] = {}
    event_sets: dict[tuple[str, int], frozenset[str]] = {}
    for expected_key in sorted(paths):
        path, _, _ = paths[expected_key]
        rows: dict[str, dict[str, str]] = {}
        deferred_targets: list[tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]] = []
        try:
            handle = open_tsv(path)
            with handle:
                reader = csv.DictReader(handle, delimiter="\t")
                if tuple(reader.fieldnames or ()) != ORACLE_FIELDS:
                    fail("ORACLE_SCHEMA_GATE")
                for row in reader:
                    if set(row) != set(ORACLE_FIELDS):
                        fail("ORACLE_SCHEMA_GATE")
                    world = row["world_id"]
                    seed = parse_seed(row["corpus_seed"], "ORACLE_SEED_GATE")
                    if (world, seed) != expected_key:
                        fail("ORACLE_PROVENANCE_GATE")
                    event_id = validate_event_id(row["event_id"], "ORACLE_EVENT_ID_GATE")
                    if event_id in rows:
                        fail("ORACLE_DUPLICATE_EVENT_GATE")
                    validate_oracle_scalar_fields(row)
                    rows[event_id] = {field: row[field] for field in TRUTH_CLUSTER_FIELDS}
                    deferred_targets.append((
                        valid_pipe_value(row["relation_target_event_id"], "ORACLE_TARGET_GATE"),
                        valid_pipe_value(row["scope_start_event_id"], "ORACLE_SCOPE_GATE"),
                        valid_pipe_value(row["scope_end_event_id"], "ORACLE_SCOPE_GATE"),
                    ))
        except (csv.Error, UnicodeError, EOFError):
            fail("ORACLE_TSV_PARSE_GATE")
        if not 8448 <= len(rows) <= 8512:
            fail("ORACLE_EVENT_COUNT_GATE")
        manifest_events = parse_seed(held_rows[expected_key]["events"], "ORACLE_EVENT_COUNT_GATE")
        if len(rows) != manifest_events:
            fail("ORACLE_EVENT_COUNT_GATE")
        ids = frozenset(rows)
        for relation, start, end in deferred_targets:
            for atoms in (relation, start, end):
                if atoms != ("NONE",) and any(atom not in ids for atom in atoms):
                    fail("ORACLE_TARGET_MEMBERSHIP_GATE")
            if start != ("NONE",) and len(start) != 1:
                fail("ORACLE_SCOPE_GATE")
            if end != ("NONE",) and len(end) != 1:
                fail("ORACLE_SCOPE_GATE")
            if (start == ("NONE",)) != (end == ("NONE",)):
                fail("ORACLE_SCOPE_GATE")
        if ids != authentic_events.get(expected_key):
            fail("AUTHENTIC_ORACLE_JOIN_GATE")
        if expected_key[0] in PAIR_WORLDS and not pair_events[expected_key].issubset(ids):
            fail("PAIR_ORACLE_JOIN_GATE")
        truths[expected_key] = rows
        event_sets[expected_key] = ids
    labels_and_hashes = tuple(sorted((label, digest) for _, label, digest in paths.values()))
    return OracleBundle(truths, event_sets, labels_and_hashes)


def comb2(value: int) -> int:
    return value * (value - 1) // 2


def clustering_metrics(truth: list[str], prediction: list[str | None]) -> dict[str, float | int | bool | None]:
    n = len(truth)
    truth_counts = Counter(truth)
    encoded_prediction: list[tuple[str, str | int]] = []
    resolved_n = 0
    for index, label in enumerate(prediction):
        if label is None:
            encoded_prediction.append(("ABSTENTION", index))
        else:
            encoded_prediction.append(("RESOLVED", label))
            resolved_n += 1
    pred_counts = Counter(encoded_prediction)
    cells = Counter(zip(truth, encoded_prediction))
    same_truth = sum(comb2(value) for value in truth_counts.values())
    all_pairs = comb2(n)
    different_truth = all_pairs - same_truth
    same_prediction = sum(comb2(value) for value in pred_counts.values())
    tp = sum(comb2(value) for value in cells.values())
    fp = same_prediction - tp
    fn = same_truth - tp
    pair_den = 2 * tp + fp + fn
    pair_f1 = (2 * tp / pair_den) if pair_den else None

    if n:
        mi = 0.0
        for (truth_label, pred_label), count in cells.items():
            mi += (count / n) * math.log(
                (count * n) / (truth_counts[truth_label] * pred_counts[pred_label])
            )
        truth_h = -sum((count / n) * math.log(count / n) for count in truth_counts.values())
        pred_h = -sum((count / n) * math.log(count / n) for count in pred_counts.values())
        if truth_h + pred_h == 0:
            nmi = 1.0
        else:
            nmi = 2 * mi / (truth_h + pred_h)
    else:
        nmi = None

    if all_pairs:
        sum_truth = same_truth
        sum_pred = same_prediction
        expected = sum_truth * sum_pred / all_pairs
        maximum = 0.5 * (sum_truth + sum_pred)
        ari = (tp - expected) / (maximum - expected) if maximum != expected else 1.0
    else:
        ari = None
    capacity = n >= 2 and len(truth_counts) >= 2 and same_truth > 0 and different_truth > 0
    return {
        "n": n, "classes": len(truth_counts), "resolved_n": resolved_n,
        "coverage": resolved_n / n if n else None, "nmi": nmi if capacity else None,
        "ari": ari if capacity else None, "pair_f1": pair_f1 if capacity else None,
        "same_truth_pairs": same_truth, "different_truth_pairs": different_truth,
        "co_cluster_fp": fp,
        "co_cluster_fpr": fp / different_truth if different_truth else None,
        "capacity": capacity,
    }


def primary_index(nmi: float | None, ari: float | None, pair_f1: float | None) -> float | None:
    if nmi is None or ari is None or pair_f1 is None:
        return None
    return min(nmi / 0.35, ari / 0.20, pair_f1 / 0.35)


def read_claim_predictions(info: ClaimInfo, oracle: dict[str, dict[str, str]]) -> dict[str, dict[str, Any]]:
    property_truth: dict[str, list[tuple[str, str]]] = {prop: [] for prop in SCOREABLE}
    absent: dict[str, list[str]] = {prop: [] for prop in SCOREABLE}
    try:
        handle = open_tsv(info.path)
        with handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != CLAIM_FIELDS:
                fail("CLAIM_REOPEN_SCHEMA_GATE")
            for row in reader:
                event_id = row["event_id"]
                truth_row = oracle.get(event_id)
                if truth_row is None:
                    fail("CLAIM_ORACLE_JOIN_GATE")
                for prop, (claim_field, truth_field) in SCOREABLE.items():
                    truth = truth_row[truth_field]
                    prediction = row[claim_field]
                    if truth == "NONE":
                        absent[prop].append(prediction)
                    else:
                        property_truth[prop].append((truth, prediction))
    except (csv.Error, UnicodeError, EOFError):
        fail("CLAIM_REOPEN_PARSE_GATE")

    result: dict[str, dict[str, Any]] = {}
    for prop in SCOREABLE:
        units = property_truth[prop]
        if prop == "ENTITY_REUSE":
            counts = Counter(truth for truth, _ in units)
            units = [(truth, pred) for truth, pred in units if counts[truth] >= 2]
        truth = [item[0] for item in units]
        pred = [None if item[1] == UNRESOLVED else item[1] for item in units]
        metric = clustering_metrics(truth, pred)
        absent_values = absent[prop]
        false_discoveries = sum(value != UNRESOLVED for value in absent_values)
        absent_rate = false_discoveries / len(absent_values) if absent_values else None
        applicable = [value for value in (absent_rate, metric["co_cluster_fpr"]) if value is not None]
        metric.update({
            "absent_truth_n": len(absent_values),
            "false_discoveries": false_discoveries,
            "absent_claim_rate": absent_rate,
            "false_positive_rate": max(applicable) if applicable else None,
            "unresolved_n": sum(value is None for value in pred),
        })
        result[prop] = metric
    return result


def blank_metric_values() -> dict[str, str]:
    return {field: NA for field in (
        "eligible_n", "prediction_n", "coverage", "nmi", "ari", "pair_f1",
        "balanced_accuracy", "mcc", "fdr", "top1", "mrr",
        "mrr_above_chance", "endpoint_accuracy", "exact_scope_accuracy",
        "interval_iou", "target_distance_mae", "false_discoveries",
        "absent_truth_n", "unresolved_n", "invalid_n", "co_cluster_fpr",
        "false_positive_rate", "primary_index", "threshold_pass",
    )}


def hold_panel_row(
    view: str, world: str, seed: int, representation: str, decoder: str,
    prop: str, pair: bool,
) -> dict[str, str]:
    row = {
        "view": view, "world_id": world, "corpus_seed": str(seed),
        "representation": representation, "decoder_id": decoder,
        "property": prop, "kind": "UNSCORED",
        "status": "UNSCORED_PAIR_INTERFACE_HOLD" if pair else "UNSCORED_INTERFACE_HOLD",
        "endpoint_qualification": QUALIFICATIONS[prop],
        "metric_note": "PAIR_ENDPOINTS_HARD_DISABLED_NO_RECORD_ID" if pair else "FROZEN_INTERFACE_HOLD",
    }
    row.update(blank_metric_values())
    return row


def scored_panel_row(info: ClaimInfo, prop: str, metric: dict[str, Any]) -> dict[str, str]:
    capacity = bool(metric["capacity"])
    nmi = metric["nmi"] if capacity else None
    ari = metric["ari"] if capacity else None
    pair_f1 = metric["pair_f1"] if capacity else None
    index = primary_index(nmi, ari, pair_f1)
    passed = bool(
        capacity and nmi is not None and ari is not None and pair_f1 is not None
        and nmi >= 0.35 and ari >= 0.20 and pair_f1 >= 0.35
    )
    row = {
        "view": "authentic", "world_id": info.world_id,
        "corpus_seed": str(info.seed), "representation": info.representation,
        "decoder_id": info.decoder_id, "property": prop, "kind": "CLUSTERING",
        "status": "SCORED" if capacity else "ABSENT_OR_NO_CAPACITY",
        "eligible_n": str(metric["n"]), "prediction_n": str(metric["resolved_n"]),
        "coverage": fmt_float(metric["coverage"]), "nmi": fmt_float(nmi),
        "ari": fmt_float(ari), "pair_f1": fmt_float(pair_f1),
        "balanced_accuracy": NA, "mcc": NA, "fdr": NA, "top1": NA,
        "mrr": NA, "mrr_above_chance": NA, "endpoint_accuracy": NA,
        "exact_scope_accuracy": NA, "interval_iou": NA,
        "target_distance_mae": NA,
        "false_discoveries": str(metric["false_discoveries"]),
        "absent_truth_n": str(metric["absent_truth_n"]),
        "unresolved_n": str(metric["unresolved_n"]), "invalid_n": "0",
        "co_cluster_fpr": fmt_float(metric["co_cluster_fpr"]),
        "false_positive_rate": fmt_float(metric["false_positive_rate"]),
        "primary_index": fmt_float(index), "threshold_pass": bool_text(passed),
        "endpoint_qualification": QUALIFICATIONS[prop],
        "metric_note": "PRIVATE_PER_EVENT_ABSTENTION_SINGLETONS",
    }
    return row


def compute_panel_rows(
    authentic: list[ClaimInfo], pairs: list[ClaimInfo],
    oracles: OracleBundle,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[tuple[str, int, str, str, str], dict[str, Any]]]:
    panel: list[dict[str, str]] = []
    metrics: dict[tuple[str, int, str, str, str], dict[str, Any]] = {}
    for info in sorted(authentic, key=lambda x: (x.world_id, x.seed, x.representation, x.decoder_id)):
        measured = read_claim_predictions(info, oracles.truths[(info.world_id, info.seed)])
        for prop in ALL_PROPERTIES:
            if prop in SCOREABLE:
                metric = measured[prop]
                panel.append(scored_panel_row(info, prop, metric))
                metrics[(info.world_id, info.seed, info.representation, info.decoder_id, prop)] = metric
            else:
                panel.append(hold_panel_row(
                    "authentic", info.world_id, info.seed, info.representation,
                    info.decoder_id, prop, False,
                ))
    pair_panel = [
        hold_panel_row("pair", info.world_id, info.seed, info.representation,
                       info.decoder_id, prop, True)
        for info in sorted(pairs, key=lambda x: (x.world_id, x.seed, x.representation, x.decoder_id))
        for prop in ALL_PROPERTIES
    ]
    return panel, pair_panel, metrics


def decoder_seed_aggregate(
    metrics: dict[tuple[str, int, str, str, str], dict[str, Any]],
    world: str, representation: str, decoder: str, prop: str,
) -> dict[str, Any]:
    rows = [metrics[(world, seed, representation, decoder, prop)] for seed in HELD_SEEDS]
    passes = [bool(
        row["capacity"] and row["nmi"] is not None and row["ari"] is not None
        and row["pair_f1"] is not None and row["nmi"] >= 0.35
        and row["ari"] >= 0.20 and row["pair_f1"] >= 0.35
    ) for row in rows]
    aggregate = {
        "seed_passes": sum(passes), "clear": sum(passes) >= 3,
    }
    for name in ("coverage", "nmi", "ari", "pair_f1", "co_cluster_fpr", "false_positive_rate"):
        aggregate[name] = median_or_none(row[name] for row in rows)
    aggregate["primary_index"] = median_or_none(
        primary_index(row["nmi"], row["ari"], row["pair_f1"]) for row in rows
    )
    return aggregate


def compute_world_rows(
    metrics: dict[tuple[str, int, str, str, str], dict[str, Any]],
    implementations: dict[str, dict],
) -> tuple[list[dict[str, str]], dict[tuple[str, str, str], dict[str, Any]]]:
    decoders = sorted(implementations)
    rows: list[dict[str, str]] = []
    aggregates: dict[tuple[str, str, str], dict[str, Any]] = {}
    for prop in ALL_PROPERTIES:
        for world in WORLDS:
            for representation in REPRESENTATIONS:
                if prop not in SCOREABLE:
                    row = {field: NA for field in WORLD_REP_FIELDS}
                    row.update({
                        "view": "authentic", "property": prop, "world_id": world,
                        "representation": representation,
                        "status": "UNSCORED_INTERFACE_HOLD",
                        "decoders_scored": "0", "decoders_clear": "0",
                        "luna_decoders_clear": "0", "median_decoder_clear": "false",
                        "endpoint_qualification": QUALIFICATIONS[prop],
                    })
                    rows.append(row)
                    continue
                per_decoder = {
                    decoder: decoder_seed_aggregate(metrics, world, representation, decoder, prop)
                    for decoder in decoders
                }
                clear = [decoder for decoder, value in per_decoder.items() if value["clear"]]
                luna_clear = [decoder for decoder in clear
                              if implementations[decoder]["model_family"] == "LUNA"]
                world_clear = len(clear) >= 3 and len(luna_clear) >= 2
                coordinate = {
                    name: median_or_none(value[name] for value in per_decoder.values())
                    for name in ("coverage", "nmi", "ari", "pair_f1", "primary_index",
                                 "false_positive_rate", "co_cluster_fpr")
                }
                aggregate = {
                    "per_decoder": per_decoder, "decoders_clear": tuple(clear),
                    "luna_clear": tuple(luna_clear), "world_clear": world_clear,
                    **coordinate,
                }
                aggregates[(prop, world, representation)] = aggregate
                row = {field: NA for field in WORLD_REP_FIELDS}
                row.update({
                    "view": "authentic", "property": prop, "world_id": world,
                    "representation": representation, "status": "SCORED",
                    "decoders_scored": str(len(decoders)),
                    "decoders_clear": str(len(clear)),
                    "luna_decoders_clear": str(len(luna_clear)),
                    "median_decoder_clear": bool_text(world_clear),
                    "endpoint_qualification": QUALIFICATIONS[prop],
                    "coverage": fmt_float(coordinate["coverage"]),
                    "nmi": fmt_float(coordinate["nmi"]), "ari": fmt_float(coordinate["ari"]),
                    "pair_f1": fmt_float(coordinate["pair_f1"]),
                    "primary_index": fmt_float(coordinate["primary_index"]),
                    "false_positive_rate": fmt_float(coordinate["false_positive_rate"]),
                    "co_cluster_fpr": fmt_float(coordinate["co_cluster_fpr"]),
                })
                rows.append(row)
    return rows, aggregates


def exact_upper95(values: list[float]) -> float:
    if len(values) != 5:
        fail("W10_SEED_VECTOR_GATE")
    statistics_vector = [
        float(statistics.median(values[index] for index in sample))
        for sample in itertools.product(range(5), repeat=5)
    ]
    statistics_vector.sort()
    index = math.ceil(0.95 * len(statistics_vector)) - 1
    return statistics_vector[index]


def compute_w10_rows(
    metrics: dict[tuple[str, int, str, str, str], dict[str, Any]],
    implementations: dict[str, dict],
) -> tuple[list[dict[str, str]], dict[tuple[str, str], dict[str, Any]]]:
    decoders = sorted(implementations)
    rows: list[dict[str, str]] = []
    diagnostics: dict[tuple[str, str], dict[str, Any]] = {}
    for prop in SCOREABLE:
        for representation in REPRESENTATIONS:
            seed_rates: list[float] = []
            complete = True
            for seed in HELD_SEEDS:
                rates = [metrics[("W10", seed, representation, decoder, prop)]["false_positive_rate"]
                         for decoder in decoders]
                if any(rate is None for rate in rates):
                    complete = False
                    break
                seed_rates.append(float(statistics.median(rates)))
            if complete:
                point = float(statistics.median(seed_rates))
                upper = exact_upper95(seed_rates)
                guard = upper <= 0.10
                encoded = "|".join(
                    f"{seed}:{fmt_float(rate)}" for seed, rate in zip(HELD_SEEDS, seed_rates)
                )
            else:
                point = upper = None
                guard = False
                encoded = NA
            diagnostic = {
                "seed_rates": seed_rates if complete else None,
                "point": point, "upper": upper, "guard": guard,
            }
            diagnostics[(prop, representation)] = diagnostic
            rows.append({
                "property": prop, "representation": representation,
                "endpoint_qualification": QUALIFICATIONS[prop], "panels": "25",
                "seed_false_positive_rates": encoded,
                "false_positive_rate": fmt_float(point),
                "false_positive_upper95": fmt_float(upper),
                "upper95_method": "EXACT_SEED_CLUSTER_BOOTSTRAP_3125_NEAREST_RANK",
                "point_guard_pass": bool_text(guard),
                "confirmatory_guard_pass": "false",
                "inference_status": "EXPLORATORY_UNCONFIRMED",
            })
    return rows, diagnostics


def choose_representation(
    prop: str, aggregates: dict[tuple[str, str, str], dict[str, Any]],
    w10: dict[tuple[str, str], dict[str, Any]],
) -> tuple[str, list[str], dict[str, Any]]:
    candidates = []
    for order, representation in enumerate(REPRESENTATIONS):
        clear_worlds = [world for world in WORLDS
                        if aggregates[(prop, world, representation)]["world_clear"]]
        meaningful = [world for world in clear_worlds if world != "W10"]
        guard = w10[(prop, representation)]
        upper = guard["upper"] if guard["upper"] is not None else math.inf
        candidates.append((
            int(guard["guard"]), len(meaningful), -upper, -order,
            representation, clear_worlds, guard,
        ))
    chosen = max(candidates)
    return chosen[4], chosen[5], chosen[6]


def compute_decision_rows(
    aggregates: dict[tuple[str, str, str], dict[str, Any]],
    w10: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for prop in ALL_PROPERTIES:
        if prop not in SCOREABLE:
            rows.append({
                "property": prop, "decision": "UNSCORED_INTERFACE_HOLD",
                "endpoint_qualification": QUALIFICATIONS[prop],
                "exploratory_pattern": "UNSCORED_INTERFACE_HOLD",
                "representation": "ALL", "worlds_clear": NA,
                "meaningful_worlds_clear": NA, "clear_world_ids": "NONE",
                "clear_world_families": NA, "w10_false_positive_rate": NA,
                "w10_false_positive_upper95": NA, "w10_guard_pass": "false",
                "organic_confusion_flag": "UNSCORED_INTERFACE_HOLD",
                "organic_confusion_representations": "NONE", "raw_p_value": NA,
                "holm_adjusted_p_value": NA, "inference_status": "UNSCORED_INTERFACE_HOLD",
            })
            continue
        representation, clear_worlds, guard = choose_representation(prop, aggregates, w10)
        meaningful = [world for world in clear_worlds if world in MEANINGFUL_WORLDS]
        if guard["guard"] and len(meaningful) >= 7:
            pattern = "POINT_THRESHOLD_GENERAL_PATTERN"
        elif guard["guard"] and 2 <= len(meaningful) <= 6:
            pattern = "POINT_THRESHOLD_FAMILY_SPECIFIC_PATTERN"
        else:
            pattern = "NO_POINT_THRESHOLD_PATTERN"
        rows.append({
            "property": prop, "decision": "EXPLORATORY_UNCONFIRMED",
            "endpoint_qualification": QUALIFICATIONS[prop],
            "exploratory_pattern": pattern, "representation": representation,
            "worlds_clear": str(len(clear_worlds)),
            "meaningful_worlds_clear": str(len(meaningful)),
            "clear_world_ids": "|".join(clear_worlds) if clear_worlds else "NONE",
            "clear_world_families": NA,
            "w10_false_positive_rate": fmt_float(guard["point"]),
            "w10_false_positive_upper95": fmt_float(guard["upper"]),
            "w10_guard_pass": bool_text(bool(guard["guard"])),
            "organic_confusion_flag": "UNSCORED_PAIR_INTERFACE_HOLD",
            "organic_confusion_representations": "NONE", "raw_p_value": NA,
            "holm_adjusted_p_value": NA,
            "inference_status": "EXPLORATORY_UNCONFIRMED_NO_FROZEN_RECORD_BLOCK_NULLS",
        })
    return rows


def normalize_world_boolean(value: Any) -> bool | None:
    if value == UNRESOLVED:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
        return number >= 0.5
    if isinstance(value, str):
        upper = value.upper()
        if upper in {"HIGH", "TRUE"}:
            return True
        if upper in {"LOW", "FALSE"}:
            return False
        if upper == "MEDIUM":
            return None
    return None


def binary_scores(tp: int, fp: int, tn: int, fn: int) -> tuple[float | None, float | None, float | None]:
    tpr = tp / (tp + fn) if tp + fn else None
    tnr = tn / (tn + fp) if tn + fp else None
    ba = (tpr + tnr) / 2 if tpr is not None and tnr is not None else None
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / denominator if denominator else None
    fdr = fp / (tp + fp) if tp + fp else None
    return ba, mcc, fdr


def compute_architecture_rows(
    world_claims: dict[tuple[str, str], WorldClaim], implementations: dict[str, dict],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    endpoint_fields = {
        "ARCHITECTURE_CLUSTER": "architecture_cluster",
        "LANGUAGE_LIKE": "language_like", "NOTATION_LIKE": "notation_like",
        "CODEBOOK_LIKE": "codebook_like", "SEMANTICS_LIGHT_LIKE": "semantics_light_like",
    }
    for decoder in sorted(implementations):
        for endpoint, field in endpoint_fields.items():
            if endpoint != "SEMANTICS_LIGHT_LIKE":
                rows.append({
                    "decoder_id": decoder, "endpoint": endpoint,
                    "truth_basis": (
                        "UNSCORED_NO_FROZEN_FAMILY_MAP" if endpoint == "ARCHITECTURE_CLUSTER"
                        else "UNSCORED_PROXY_NO_FROZEN_MAPPING"
                    ),
                    "n": "0", "nmi": NA, "ari": NA, "pair_f1": NA,
                    "balanced_accuracy": NA, "mcc": NA, "fdr": NA,
                })
                continue
            tp = fp = tn = fn = resolved = 0
            for world in WORLDS:
                prediction = normalize_world_boolean(world_claims[(world, decoder)].claim[field])
                truth = world == "W10"
                if prediction is None:
                    if truth:
                        fn += 1
                    else:
                        fp += 1
                else:
                    resolved += 1
                    if prediction and truth:
                        tp += 1
                    elif prediction and not truth:
                        fp += 1
                    elif not prediction and truth:
                        fn += 1
                    else:
                        tn += 1
            ba, mcc, fdr = binary_scores(tp, fp, tn, fn)
            rows.append({
                "decoder_id": decoder, "endpoint": endpoint,
                "truth_basis": "W10_ONLY_DIRECT_FROZEN_TRUTH_ADVERSARIAL_ABSTENTION_COMPLETION",
                "n": "10", "nmi": NA, "ari": NA, "pair_f1": NA,
                "balanced_accuracy": fmt_float(ba), "mcc": fmt_float(mcc),
                "fdr": fmt_float(fdr),
            })
    return rows


def stress_rows() -> list[dict[str, str]]:
    return [{"stress_test": name, "status": "UNSCORED_NO_EXPLICIT_DECODER_PREDICTIONS"}
            for name in STRESS_TESTS]


NUMERIC_FIELDS = {
    "coverage", "nmi", "ari", "pair_f1", "balanced_accuracy", "mcc", "fdr",
    "top1", "mrr", "mrr_above_chance", "endpoint_accuracy",
    "exact_scope_accuracy", "interval_iou", "target_distance_mae",
    "co_cluster_fpr", "false_positive_rate", "primary_index",
    "w10_false_positive_rate", "w10_false_positive_upper95",
    "false_positive_upper95",
}
INTEGER_FIELDS = {
    "eligible_n", "prediction_n", "false_discoveries", "absent_truth_n",
    "unresolved_n", "invalid_n", "decoders_scored", "decoders_clear",
    "luna_decoders_clear", "worlds_clear", "meaningful_worlds_clear", "panels", "n",
}


def compare_scalar(field: str, actual: str, expected: str, code: str) -> None:
    if expected == NA:
        if actual != NA:
            fail(code)
        return
    if field in INTEGER_FIELDS:
        if not re.fullmatch(r"(?:0|[1-9][0-9]*)", actual) or int(actual) != int(expected):
            fail(code)
        return
    if field in NUMERIC_FIELDS:
        number = parse_finite(actual, code)
        target = float(expected)
        if not math.isclose(number, target, rel_tol=1e-10, abs_tol=1e-12):
            fail(code)
        return
    if actual != expected:
        fail(code)


def compare_table(
    path: Path, fields: tuple[str, ...], expected_rows: list[dict[str, str]],
    key_fields: tuple[str, ...], code: str,
) -> int:
    expected = {}
    for row in expected_rows:
        if set(row) != set(fields):
            fail("INTERNAL_EXPECTED_SCHEMA_GATE")
        key = tuple(row[field] for field in key_fields)
        if key in expected:
            fail("INTERNAL_EXPECTED_DUPLICATE_GATE")
        expected[key] = row
    seen = set()
    try:
        handle = open_tsv(path)
        with handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != fields:
                fail(code)
            count = 0
            for row in reader:
                count += 1
                if set(row) != set(fields):
                    fail(code)
                key = tuple(row[field] for field in key_fields)
                if key in seen or key not in expected:
                    fail(code)
                seen.add(key)
                target = expected[key]
                for field in fields:
                    compare_scalar(field, row[field], target[field], code)
    except (csv.Error, UnicodeError, EOFError):
        fail(code)
    if seen != set(expected):
        fail(code)
    return count


def aggregate_binding_hash(values: Iterable[tuple[str, str]]) -> str:
    mapping = {label: digest for label, digest in values}
    return hashlib.sha256(canonical_json_bytes(mapping)).hexdigest()


def expected_summary(
    freeze_hash: str, validation_hash: str, manifest_hash: str,
    bindings: dict[str, list[tuple[str, str]]], oracles: OracleBundle,
    decisions: list[dict[str, str]],
) -> dict[str, Any]:
    decision_map = {
        row["property"]: {
            "decision": row["decision"],
            "exploratory_pattern": row["exploratory_pattern"],
            "representation": row["representation"],
        }
        for row in decisions
    }
    return {
        "schema": "GDT395_IDENTIFIABILITY_SCORE_SUMMARY_V1",
        "status": "PASS",
        "panel": {
            "worlds": 10, "held_seeds": 5, "representations": 6,
            "decoders": 5, "scoreable_properties": 7,
            "interface_hold_properties": 10,
            "authentic_claim_files": 1500, "pair_claim_files": 600,
            "world_claim_files": 50, "held_oracle_files": 50,
        },
        "input_sha256": {
            "claims_freeze": freeze_hash,
            "claims_validation": validation_hash,
            "corpus_manifest": manifest_hash,
            "authentic_event_claims": aggregate_binding_hash(bindings["authentic_event_claims"]),
            "pair_event_claims": aggregate_binding_hash(bindings["pair_event_claims"]),
            "world_claims": aggregate_binding_hash(bindings["world_claims"]),
            "held_oracles": aggregate_binding_hash(oracles.labels_and_hashes),
        },
        "decisions": decision_map,
        "endpoint_qualification": dict(QUALIFICATIONS),
        "interface_hold_properties": list(HOLD_PROPERTIES),
        "confirmatory_promotions_enabled": False,
        "unscored_method_stress_tests": list(STRESS_TESTS),
        "ambiguities": [
            "NO_RECORD_ID_IN_ACCEPTED_SCORER_INPUT",
            "NO_FROZEN_RECORD_BLOCK_NULLS",
            "NO_9999_LOCALITY_PRESERVING_PERMUTATIONS",
            "NO_RANKED_TARGET_INTERFACE",
            "PAIR_ENDPOINTS_HARD_DISABLED",
        ],
        "contains_event_rows": False,
        "voynich_rows": 0,
    }


def compare_json_exact(actual: Any, expected: Any, code: str) -> None:
    if type(actual) is not type(expected):
        fail(code)
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            fail(code)
        for key in expected:
            compare_json_exact(actual[key], expected[key], code)
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            fail(code)
        for left, right in zip(actual, expected):
            compare_json_exact(left, right, code)
    elif isinstance(expected, float):
        if not math.isclose(float(actual), expected, rel_tol=1e-10, abs_tol=1e-12):
            fail(code)
    elif actual != expected:
        fail(code)


def validate_output_directory(
    output_dir: Path, panel_rows: list[dict[str, str]], pair_rows: list[dict[str, str]],
    world_rows: list[dict[str, str]], decisions: list[dict[str, str]],
    w10_rows: list[dict[str, str]], architecture: list[dict[str, str]],
    stress: list[dict[str, str]], summary: dict[str, Any],
) -> tuple[dict[str, str], dict[str, int]]:
    try:
        if not output_dir.is_dir() or output_dir.is_symlink():
            fail("SCORER_OUTPUT_DIRECTORY_GATE")
        entries = {path.name: path for path in output_dir.iterdir()}
    except OSError:
        fail("SCORER_OUTPUT_DIRECTORY_GATE")
    if set(entries) != set(OUTPUT_FILES):
        fail("SCORER_OUTPUT_FILE_SET_GATE")
    if any(not path.is_file() or path.is_symlink() for path in entries.values()):
        fail("SCORER_OUTPUT_FILE_SET_GATE")

    row_counts = {
        "panel_metrics.tsv": compare_table(
            entries["panel_metrics.tsv"], PANEL_FIELDS, panel_rows,
            ("view", "world_id", "corpus_seed", "representation", "decoder_id", "property"),
            "PANEL_METRICS_MISMATCH_GATE",
        ),
        "pair_panel_metrics.tsv": compare_table(
            entries["pair_panel_metrics.tsv"], PANEL_FIELDS, pair_rows,
            ("view", "world_id", "corpus_seed", "representation", "decoder_id", "property"),
            "PAIR_PANEL_HOLD_GATE",
        ),
        "world_representation_metrics.tsv": compare_table(
            entries["world_representation_metrics.tsv"], WORLD_REP_FIELDS, world_rows,
            ("view", "property", "world_id", "representation"),
            "WORLD_REPRESENTATION_MISMATCH_GATE",
        ),
        "property_decisions.tsv": compare_table(
            entries["property_decisions.tsv"], DECISION_FIELDS, decisions,
            ("property",), "PROPERTY_DECISION_MISMATCH_GATE",
        ),
        "w10_false_discoveries.tsv": compare_table(
            entries["w10_false_discoveries.tsv"], W10_FIELDS, w10_rows,
            ("property", "representation"), "W10_DIAGNOSTIC_MISMATCH_GATE",
        ),
        "architecture_metrics.tsv": compare_table(
            entries["architecture_metrics.tsv"], ARCH_FIELDS, architecture,
            ("decoder_id", "endpoint"), "ARCHITECTURE_DIAGNOSTIC_MISMATCH_GATE",
        ),
        "method_stress_tests.tsv": compare_table(
            entries["method_stress_tests.tsv"], STRESS_FIELDS, stress,
            ("stress_test",), "METHOD_STRESS_HOLD_GATE",
        ),
    }
    actual_summary = read_json(entries["summary.json"], "SUMMARY_JSON_GATE")
    if not isinstance(actual_summary, dict) or set(actual_summary) != SUMMARY_KEYS:
        fail("SUMMARY_SCHEMA_GATE")
    compare_json_exact(actual_summary, summary, "SUMMARY_CONTENT_MISMATCH_GATE")
    output_hashes = {name: sha256_file(path) for name, path in sorted(entries.items())}
    return output_hashes, row_counts


def validate_freeze_and_validation(
    root: Path, freeze_path: Path, validation_path: Path,
) -> tuple[dict, dict, dict[str, list[tuple[str, str]]], dict[str, dict]]:
    freeze = read_json(freeze_path, "CLAIMS_FREEZE_JSON_GATE")
    validation = read_json(validation_path, "CLAIMS_VALIDATION_JSON_GATE")
    validate_content_hash(freeze, "CLAIMS_FREEZE_CONTENT_HASH_GATE")
    validate_content_hash(validation, "CLAIMS_VALIDATION_CONTENT_HASH_GATE")
    if freeze.get("schema") != "GDT395_BLIND_CLAIMS_FREEZE_V2":
        fail("CLAIMS_FREEZE_SCHEMA_GATE")
    if validation.get("schema") != "GDT395_BLIND_CLAIMS_VALIDATION_V2":
        fail("CLAIMS_VALIDATION_SCHEMA_GATE")
    if freeze.get("status") != "PASS" or freeze.get("phase") != "FROZEN_BEFORE_ORACLE_ACCESS":
        fail("CLAIMS_FREEZE_STATUS_GATE")
    if freeze.get("oracle_blind") is not True:
        fail("CLAIMS_FREEZE_BLIND_GATE")
    if freeze.get("oracle_opened") is not False or freeze.get("oracle_rows_read") != 0:
        fail("CLAIMS_FREEZE_ORACLE_SEAL_GATE")
    if freeze.get("voynich_rows") != 0:
        fail("CLAIMS_FREEZE_VOYNICH_GATE")
    f84 = freeze.get("f84")
    if not isinstance(f84, dict) or not f84 or any(type(value) is not bool or value for value in f84.values()):
        fail("CLAIMS_FREEZE_F84_GATE")
    if validation.get("status") != "PASS":
        fail("CLAIMS_VALIDATION_STATUS_GATE")
    validate_checks(freeze, "CLAIMS_FREEZE_CHECK_GATE")
    validate_checks(validation, "CLAIMS_VALIDATION_CHECK_GATE")
    label, digest = validation_freeze_binding(validation)
    if label != portable_label(freeze_path, root) or digest != sha256_file(freeze_path):
        fail("VALIDATION_FREEZE_BINDING_GATE")
    bindings = freeze_claim_bindings(freeze)
    implementations = implementation_entries(freeze)
    return freeze, validation, bindings, implementations


def write_validation_result(
    path: Path, source_hash: str, input_hashes: dict[str, str],
    output_hashes: dict[str, str], row_counts: dict[str, int], oracle_rows: int,
) -> str:
    result = {
        "schema": "GDT395_IDENTIFIABILITY_INDEPENDENT_VALIDATION_V1",
        "status": "PASS",
        "checks": {
            "v2_claim_freeze_and_validation": True,
            "claim_roles_hashes_and_schemas": True,
            "oracle_manifest_binding_and_hashes": True,
            "authentic_complete_join": True,
            "pair_subset_and_all_endpoints_unscored": True,
            "seven_authentic_partitions_recomputed": True,
            "entity_reuse_recurring_truth_restriction": True,
            "ten_interface_holds_preserved": True,
            "seed_decoder_representation_two_luna_aggregation": True,
            "w10_exact_3125_diagnostics": True,
            "exploratory_only_decisions": True,
            "architecture_diagnostics": True,
            "aggregate_only_output": True,
            "no_event_row_or_voynich_leakage": True,
        },
        "validator_source_sha256": source_hash,
        "input_sha256": input_hashes,
        "scorer_output_sha256": output_hashes,
        "scorer_output_rows": row_counts,
        "oracle_rows_read": oracle_rows,
        "contains_event_rows": False,
        "voynich_rows": 0,
    }
    result["content_sha256"] = hashlib.sha256(canonical_json_bytes(result)).hexdigest()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
    except FileExistsError:
        fail("VALIDATION_OUTPUT_ONE_SHOT_GATE")
    except OSError:
        fail("VALIDATION_OUTPUT_WRITE_GATE")
    return sha256_file(path)


def self_test() -> None:
    perfect = clustering_metrics(["a", "a", "b", "b"], ["x", "x", "y", "y"])
    assert perfect["nmi"] == 1.0 and perfect["ari"] == 1.0 and perfect["pair_f1"] == 1.0
    abstain = clustering_metrics(["a", "a", "b", "b"], [None, None, None, None])
    assert abstain["pair_f1"] == 0.0 and abstain["co_cluster_fpr"] == 0.0
    mixed = clustering_metrics(["a", "a", "b", "b"], ["x", "y", "x", "y"])
    assert mixed["pair_f1"] == 0.0 and mixed["co_cluster_fpr"] == 0.5
    assert exact_upper95([0.0, 0.0, 0.0, 0.0, 1.0]) == 1.0
    assert normalize_world_boolean(0.5) is True
    assert normalize_world_boolean("MEDIUM") is None
    body = {"schema": "FABRICATED", "checks": {"x": True}}
    sealed = dict(body)
    sealed["content_sha256"] = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    validate_content_hash(sealed, "FABRICATED_HASH_GATE")
    source = Path(__file__).resolve()
    fabricated_freeze = {
        "bindings": {
            "authentic_event_claims": [{"path": "auth.tsv", "sha256": "0" * 64}],
            "pair_event_claims": [{"path": "pair.tsv", "sha256": "0" * 64}],
            "world_claims": [{"path": "world.json", "sha256": "0" * 64}],
            "implementation": {
                "hashes": {"src/validate_identifiability.py": sha256_file(source)},
            },
        },
    }
    roles = freeze_claim_bindings(fabricated_freeze)
    assert set(roles) == {"authentic_event_claims", "pair_event_claims", "world_claims"}
    require_implementation_binding(
        fabricated_freeze, ROOT, source, "FABRICATED_IMPLEMENTATION_BINDING_GATE",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Independently validate GDT395 aggregate scoring")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--claims-freeze", type=Path)
    parser.add_argument("--claims-validation", type=Path)
    parser.add_argument("--corpus-manifest", type=Path)
    parser.add_argument("--oracle-root", type=Path)
    parser.add_argument("--scorer-output-dir", type=Path)
    parser.add_argument("--validation-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        print(json.dumps({"status": "PASS", "test": "FABRICATED_SELF_TEST"}, sort_keys=True))
        return 0
    required = (
        args.claims_freeze, args.claims_validation, args.corpus_manifest,
        args.oracle_root, args.scorer_output_dir, args.validation_output,
    )
    if any(value is None for value in required):
        fail("CLI_REQUIRED_ARGUMENT_GATE")
    root = args.root.resolve(strict=True)
    freeze_path = args.claims_freeze.resolve(strict=True)
    validation_path = args.claims_validation.resolve(strict=True)
    manifest_path = args.corpus_manifest.resolve(strict=True)
    oracle_root = args.oracle_root.resolve(strict=True)
    scorer_output = args.scorer_output_dir.resolve(strict=True)
    validation_output = args.validation_output.resolve(strict=False)
    try:
        validation_output.relative_to(scorer_output)
    except ValueError:
        pass
    else:
        fail("VALIDATION_OUTPUT_SEPARATION_GATE")

    freeze, validation, bindings, implementations = validate_freeze_and_validation(
        root, freeze_path, validation_path,
    )
    authentic, pairs, world_claims = authenticate_and_validate_claims(
        root, bindings, set(implementations),
    )

    # The implementation-bound public manifest is authenticated only after all
    # blind claims pass their pre-oracle gates. Oracle files are not opened
    # until their exact manifest paths and hashes have been checked.
    require_implementation_binding(freeze, root, manifest_path, "CORPUS_MANIFEST_BINDING_GATE")
    manifest = read_corpus_manifest(manifest_path)
    auth_events = {(info.world_id, info.seed): info.event_ids for info in authentic}
    pair_events = {(info.world_id, info.seed): info.event_ids for info in pairs}
    oracles = authenticate_and_read_oracles(
        oracle_root, manifest_path, manifest, auth_events, pair_events,
    )

    panel, pair_panel, seed_metrics = compute_panel_rows(authentic, pairs, oracles)
    world_rows, world_aggregates = compute_world_rows(seed_metrics, implementations)
    w10_rows, w10_diagnostics = compute_w10_rows(seed_metrics, implementations)
    decisions = compute_decision_rows(world_aggregates, w10_diagnostics)
    architecture = compute_architecture_rows(world_claims, implementations)
    stress = stress_rows()
    freeze_hash = sha256_file(freeze_path)
    validation_hash = sha256_file(validation_path)
    manifest_hash = sha256_file(manifest_path)
    summary = expected_summary(
        freeze_hash, validation_hash, manifest_hash, bindings, oracles, decisions,
    )
    output_hashes, row_counts = validate_output_directory(
        scorer_output, panel, pair_panel, world_rows, decisions, w10_rows,
        architecture, stress, summary,
    )
    input_hashes = {
        "claims_freeze": freeze_hash, "claims_validation": validation_hash,
        "corpus_manifest": manifest_hash,
        "held_oracles": aggregate_binding_hash(oracles.labels_and_hashes),
    }
    result_hash = write_validation_result(
        validation_output, sha256_file(Path(__file__)), input_hashes,
        output_hashes, row_counts,
        sum(len(rows) for rows in oracles.truths.values()),
    )
    print(json.dumps({"status": "PASS", "validation_sha256": result_hash}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as error:
        print(json.dumps({"status": "FAIL", "gate": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
    except Exception:
        print(json.dumps({"status": "FAIL", "gate": "INTERNAL_VALIDATION_GATE"}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
