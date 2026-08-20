#!/usr/bin/env python3
"""D396S01: oracle-blind multiview record-graph decoder for GDT396.

Only visible surfaces and the physical identifiers/metadata supplied by the V2
observation interface are used.  The implementation deliberately uses no
world-specific constants, readable labels, or cross-surface correspondence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence


API_VERSION = 2
DECODER_ID = "D396S01"
SUPPORTED_REPRESENTATIONS = (
    "FULL_GROUP",
    "INFERRED_COMPONENTS",
    "RECORD_TOPOLOGY",
    "MULTI_RESOLUTION",
)
PARTITION_PROPERTIES = (
    "LEXICAL_IDENTITY",
    "SEMANTIC_ENTITY_IDENTITY",
    "HISTORICAL_ANCESTRY",
    "CURRENT_PRODUCTIVE_COMPONENT",
    "FOSSIL_COMPONENT",
    "CURRENT_SHARED_MEANING",
    "FUNCTION_OPERATOR_CLASS",
    "CONSTRUCTION_CLASS",
    "REGISTER_REALIZATION",
    "SEMANTIC_CATEGORY",
    "STATE_BEFORE_IDENTITY",
    "STATE_AFTER_IDENTITY",
    "STATE_TRANSITION_IDENTITY",
)
BINARY_PROPERTIES = (
    "PRODUCTIVE_MORPHOLOGY",
    "FOSSILIZED_MORPHOLOGY",
    "TEMPORAL_STATE_GATE",
    "ENTITY_REUSE_PRESENT",
)
TARGET_PROPERTIES = (
    "GENERIC_RELATION",
    "COORDINATOR_RELATION",
    "ALTERNATIVE_RELATION",
    "REFERENCE_ANAPHORA",
    "ENTITY_REUSE_ANTECEDENT",
)
ARCHITECTURE_PROPERTIES = (
    "LANGUAGE_LIKE",
    "NOTATION_LIKE",
    "CODEBOOK_LIKE",
    "ORGANIC_EVOLUTION_LIKE",
    "CLEAN_ENGINEERED_LIKE",
    "SEMANTICS_LIGHT_LIKE",
)
TABLES = (
    "partition_claims",
    "binary_claims",
    "target_queries",
    "target_ranks",
    "scope_claims",
    "morphology_claims",
    "record_partition_claims",
    "architecture_partition_claims",
    "architecture_binary_claims",
)
GRAPH_DIM = 96
RECORD_DIM = 24
MAX_TARGET_RANK = 5
MAX_MORPH_RANK = 3


DECODER_META = {
    "api_version": API_VERSION,
    "decoder_id": DECODER_ID,
    "designer_model": "gpt-5.6-sol",
    "method_family": "MULTIVIEW_RECORD_GRAPH",
    "oracle_blind": True,
    "supported_representations": list(SUPPORTED_REPRESENTATIONS),
    "supported_claim_kinds": [
        "partition_claims",
        "binary_claims",
        "target_queries",
        "target_ranks",
        "scope_claims",
        "morphology_claims",
        "record_partition_claims",
        "architecture_partition_claims",
        "architecture_binary_claims",
    ],
    "max_rank_by_claim_kind": {
        "GENERIC_RELATION": MAX_TARGET_RANK,
        "COORDINATOR_RELATION": MAX_TARGET_RANK,
        "ALTERNATIVE_RELATION": MAX_TARGET_RANK,
        "REFERENCE_ANAPHORA": MAX_TARGET_RANK,
        "ENTITY_REUSE_ANTECEDENT": MAX_TARGET_RANK,
        "MORPHOLOGY_ANALYSIS": MAX_MORPH_RANK,
    },
    "fit_scope": "TRAIN_ONLY_WORLD",
    "transductive_within_held_seed": True,
}


def _outputs() -> dict[str, list[dict]]:
    return {name: [] for name in TABLES}


def _surface_key(surface: Sequence[Any]) -> str:
    return json.dumps(list(surface), ensure_ascii=False, separators=(",", ":"))


def _surface_from_key(key: str) -> tuple[Any, ...]:
    return tuple(json.loads(key))


def _digest(text: str, size: int = 12) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:size]


def _anon(prefix: str, payload: str) -> str:
    return f"{prefix}_{_digest(payload)}"


def _bucket(text: str, width: int) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16) % width


def _clip01(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 8)


def _safe_log2(value: float) -> float:
    return math.log2(max(value, 1e-12))


def _phase_from_seed(seed: int) -> str:
    if 3960000 <= seed <= 3960999:
        return "DEVELOPMENT"
    if 3961000 <= seed <= 3961999:
        return "QUALIFICATION"
    return "CONFIRMATION"


def _ordered(rows: Sequence[dict]) -> list[dict]:
    return sorted(
        rows,
        key=lambda row: (
            int(row.get("global_event_rank", row.get("event_index", 0))),
            str(row["event_id"]),
        ),
    )


def _group_records(rows: Sequence[dict]) -> dict[str, list[dict]]:
    records: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        records[str(row["record_id"])].append(row)
    return {
        record_id: sorted(
            events,
            key=lambda row: (int(row["record_event_ordinal"]), str(row["event_id"])),
        )
        for record_id, events in records.items()
    }


def _event_views(rows: Sequence[dict]) -> tuple[
    dict[str, list[float]], dict[str, int], dict[str, set[str]], dict[str, int]
]:
    """Build stable hashed type-context features from one visible channel."""

    ordered = _ordered(rows)
    records = _group_records(ordered)
    counts = Counter(_surface_key(row["visible_surface"]) for row in ordered)
    type_records: dict[str, set[str]] = defaultdict(set)
    within_reuses: Counter[str] = Counter()
    raw: dict[str, list[float]] = {key: [0.0] * GRAPH_DIM for key in counts}

    event_prev: dict[str, str | None] = {}
    event_next: dict[str, str | None] = {}
    event_record_pos: dict[str, tuple[int, int]] = {}
    event_line_pos: dict[str, tuple[int, int]] = {}

    for record_events in records.values():
        seen: set[str] = set()
        line_groups: dict[str, list[dict]] = defaultdict(list)
        for event in record_events:
            line_groups[str(event["line_id"])].append(event)
        line_pos: dict[str, tuple[int, int]] = {}
        for line_events in line_groups.values():
            line_events.sort(key=lambda row: int(row["record_event_ordinal"]))
            for index, event in enumerate(line_events):
                line_pos[str(event["event_id"])] = (index, len(line_events))
        for index, event in enumerate(record_events):
            event_id = str(event["event_id"])
            key = _surface_key(event["visible_surface"])
            event_prev[event_id] = (
                _surface_key(record_events[index - 1]["visible_surface"]) if index else None
            )
            event_next[event_id] = (
                _surface_key(record_events[index + 1]["visible_surface"])
                if index + 1 < len(record_events)
                else None
            )
            event_record_pos[event_id] = (index, len(record_events))
            event_line_pos[event_id] = line_pos[event_id]
            type_records[key].add(str(event["record_id"]))
            if key in seen:
                within_reuses[key] += 1
            seen.add(key)

    n_rows = max(1, len(ordered))
    n_records = max(1, len(records))
    for row in ordered:
        event_id = str(row["event_id"])
        key = _surface_key(row["visible_surface"])
        vector = raw[key]
        rec_index, rec_len = event_record_pos[event_id]
        line_index, line_len = event_line_pos[event_id]
        vector[3] += 1.0 if str(row.get("ambiguous_boundary", "FALSE")).upper() == "TRUE" else 0.0
        vector[4] += 1.0 if rec_index == 0 else 0.0
        vector[5] += 1.0 if rec_index + 1 == rec_len else 0.0
        vector[6] += 1.0 if line_index == 0 else 0.0
        vector[7] += 1.0 if line_index + 1 == line_len else 0.0
        vector[8] += rec_index / max(1, rec_len - 1)
        vector[9] += line_index / max(1, line_len - 1)

        for offset, width, field in (
            (10, 8, "separator_before"),
            (18, 8, "separator_after"),
            (26, 6, "register_id"),
            (32, 4, "hand_id"),
            (36, 6, "layout_role"),
            (42, 6, "record_position_bin"),
            (48, 6, "line_position_bin"),
        ):
            value = f"{field}:{row.get(field, '')}"
            vector[offset + _bucket(value, width)] += 1.0
        prev_key = event_prev[event_id]
        next_key = event_next[event_id]
        if prev_key is not None:
            vector[54 + _bucket(prev_key, 18)] += 1.0
        if next_key is not None:
            vector[72 + _bucket(next_key, 18)] += 1.0
        vector[90 + _bucket(str(row["line_id"]), 3)] += 1.0
        vector[93 + _bucket(str(row["paragraph_id"]), 3)] += 1.0

    features: dict[str, list[float]] = {}
    for key, count in counts.items():
        vector = raw[key]
        denom = float(count)
        for index in range(3, GRAPH_DIM):
            vector[index] /= denom
        vector[0] = math.log1p(count) / math.log1p(n_rows)
        vector[1] = len(type_records[key]) / n_records
        vector[2] = len(_surface_from_key(key)) / 16.0
        vector[3] = vector[3]
        # Reuse strength replaces one redundant hashed paragraph channel.
        vector[95] = within_reuses[key] / denom
        features[key] = vector
    return features, dict(counts), type_records, dict(within_reuses)


def _means_scales(vectors: Sequence[Sequence[float]]) -> tuple[list[float], list[float]]:
    if not vectors:
        return [0.0] * GRAPH_DIM, [1.0] * GRAPH_DIM
    dims = len(vectors[0])
    means = [sum(row[index] for row in vectors) / len(vectors) for index in range(dims)]
    scales = []
    for index, mean in enumerate(means):
        variance = sum((row[index] - mean) ** 2 for row in vectors) / len(vectors)
        scales.append(max(math.sqrt(variance), 1e-6))
    return means, scales


def _standardize(vector: Sequence[float], means: Sequence[float], scales: Sequence[float]) -> list[float]:
    # Clipping prevents rare held metadata buckets from dominating a cluster.
    return [max(-5.0, min(5.0, (value - mean) / scale)) for value, mean, scale in zip(vector, means, scales)]


def _distance2(left: Sequence[float], right: Sequence[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right))


def _nearest(vector: Sequence[float], centroids: Sequence[Sequence[float]]) -> tuple[int, float, float]:
    distances = [_distance2(vector, center) for center in centroids]
    ranked = sorted(range(len(distances)), key=lambda index: (distances[index], index))
    first = ranked[0]
    second_distance = distances[ranked[1]] if len(ranked) > 1 else distances[first] + 1.0
    return first, distances[first], second_distance


def _kmeans(
    items: Sequence[tuple[str, Sequence[float]]], clusters: int, iterations: int = 30
) -> tuple[list[list[float]], dict[str, int]]:
    if not items:
        return [[0.0]], {}
    ordered = sorted(items, key=lambda item: item[0])
    clusters = max(1, min(clusters, len(ordered)))
    centers = [list(ordered[0][1])]
    chosen = {ordered[0][0]}
    while len(centers) < clusters:
        candidates = []
        for key, vector in ordered:
            if key in chosen:
                continue
            distance = min(_distance2(vector, center) for center in centers)
            candidates.append((distance, key, vector))
        _, key, vector = max(candidates, key=lambda item: (item[0], item[1]))
        chosen.add(key)
        centers.append(list(vector))

    labels: dict[str, int] = {}
    for _ in range(iterations):
        new_labels = {key: _nearest(vector, centers)[0] for key, vector in ordered}
        if new_labels == labels:
            break
        labels = new_labels
        sums = [[0.0] * len(centers[0]) for _ in centers]
        sizes = [0] * len(centers)
        for key, vector in ordered:
            label = labels[key]
            sizes[label] += 1
            for index, value in enumerate(vector):
                sums[label][index] += value
        for label in range(len(centers)):
            if sizes[label]:
                centers[label] = [value / sizes[label] for value in sums[label]]
    labels = {key: _nearest(vector, centers)[0] for key, vector in ordered}
    return [[round(value, 10) for value in center] for center in centers], labels


def _find_occurrences(surface: Sequence[Any], component: Sequence[Any]) -> list[int]:
    width = len(component)
    if not width or width > len(surface):
        return []
    return [
        index
        for index in range(len(surface) - width + 1)
        if tuple(surface[index:index + width]) == tuple(component)
    ]


def _infer_components(
    rows: Sequence[dict], type_labels: dict[str, int]
) -> tuple[list[dict], dict[str, list[dict]]]:
    surface_id = str(rows[0]["surface_id"])
    minimum_width = 1 if surface_id == "FREE_SURFACE" else 2
    maximum_width = 4 if surface_id == "FREE_SURFACE" else 8
    type_rows: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        type_rows[_surface_key(row["visible_surface"])].append(row)

    component_types: dict[str, set[str]] = defaultdict(set)
    component_positions: dict[str, Counter[str]] = defaultdict(Counter)
    component_residuals: dict[str, set[str]] = defaultdict(set)
    component_atoms: dict[str, tuple[Any, ...]] = {}
    for type_key in sorted(type_rows):
        surface = _surface_from_key(type_key)
        upper = min(maximum_width, len(surface) - 1)
        if upper < minimum_width:
            continue
        seen: set[tuple[str, int]] = set()
        for width in range(minimum_width, upper + 1):
            for start in range(len(surface) - width + 1):
                atoms = surface[start:start + width]
                component_key = _surface_key(atoms)
                marker = (component_key, start)
                if marker in seen:
                    continue
                seen.add(marker)
                component_atoms[component_key] = atoms
                component_types[component_key].add(type_key)
                if start == 0:
                    component_positions[component_key]["P"] += 1
                if start + width == len(surface):
                    component_positions[component_key]["S"] += 1
                if start and start + width < len(surface):
                    component_positions[component_key]["I"] += 1
                residual = surface[:start] + ("#",) + surface[start + width:]
                component_residuals[component_key].add(_surface_key(residual))

    n_types = max(1, len(type_rows))
    average_length = sum(len(_surface_from_key(key)) for key in type_rows) / n_types
    accepted: list[dict] = []
    maximum_support = max(12, int(math.ceil(0.20 * n_types)))
    for component_key in sorted(component_types):
        members = component_types[component_key]
        type_support = len(members)
        if not 3 <= type_support <= maximum_support:
            continue
        records = {
            str(row["record_id"])
            for member in members
            for row in type_rows[member]
        }
        if len(records) < 2:
            continue
        atoms = component_atoms[component_key]
        positions = component_positions[component_key]
        position_consistency = max(positions.get("P", 0), positions.get("S", 0)) / type_support
        support_score = min(1.0, math.log2(type_support) / 4.0)
        length_score = min(1.0, len(atoms) / max(1.0, average_length * 0.60))
        specificity = 1.0 - type_support / n_types
        residual_score = min(1.0, len(component_residuals[component_key]) / 5.0)
        label_counts = Counter(type_labels.get(member, -1) for member in members)
        community_concentration = max(label_counts.values(), default=0) / type_support
        current_score = (
            0.25 * support_score
            + 0.24 * position_consistency
            + 0.20 * length_score
            + 0.16 * specificity
            + 0.15 * residual_score
        )
        fossil_score = (
            0.24 * support_score
            + 0.24 * length_score
            + 0.32 * community_concentration
            + 0.20 * (1.0 - position_consistency)
        )
        status: str | None = None
        score = 0.0
        if current_score >= 0.68 and position_consistency >= 0.50:
            status, score = "CURRENTLY_PRODUCTIVE", current_score
        elif fossil_score >= 0.76 and position_consistency < 0.50 and type_support <= 20:
            status, score = "FOSSILIZED", fossil_score
        if status is None:
            continue
        accepted.append(
            {
                "component_id": _anon("M", component_key),
                "atoms": list(atoms),
                "status": status,
                "score": round(score, 8),
                "type_support": type_support,
                "record_support": len(records),
            }
        )

    # Retain a compact, diverse component vocabulary learned on training only.
    accepted.sort(
        key=lambda item: (
            -float(item["score"]),
            -len(item["atoms"]),
            str(item["component_id"]),
        )
    )
    selected: list[dict] = []
    per_initial: Counter[str] = Counter()
    for item in accepted:
        initial = _surface_key(item["atoms"][:1])
        if per_initial[initial] >= 24:
            continue
        per_initial[initial] += 1
        selected.append(item)
        if len(selected) >= 384:
            break

    type_components: dict[str, list[dict]] = defaultdict(list)
    for type_key in type_rows:
        surface = _surface_from_key(type_key)
        for item in selected:
            offsets = _find_occurrences(surface, item["atoms"])
            if not offsets:
                continue
            start = offsets[0]
            type_components[type_key].append(
                {
                    "component_id": item["component_id"],
                    "start": start,
                    "end": start + len(item["atoms"]),
                    "status": item["status"],
                    "score": item["score"],
                }
            )
        type_components[type_key].sort(
            key=lambda hit: (
                -float(hit["score"]),
                -(int(hit["end"]) - int(hit["start"])),
                str(hit["component_id"]),
            )
        )
    return selected, {key: value[:MAX_MORPH_RANK] for key, value in type_components.items()}


def _record_vector(
    events: Sequence[dict], type_clusters: dict[str, int], type_components: dict[str, list[dict]]
) -> list[float]:
    vector = [0.0] * RECORD_DIM
    length = max(1, len(events))
    keys = [_surface_key(row["visible_surface"]) for row in events]
    counts = Counter(keys)
    lines = {str(row["line_id"]) for row in events}
    vector[0] = math.log1p(length)
    vector[1] = len(lines) / length
    vector[2] = len(counts) / length
    vector[3] = sum(count - 1 for count in counts.values()) / length
    vector[4] = sum(1 for row in events if str(row.get("ambiguous_boundary", "FALSE")).upper() == "TRUE") / length
    vector[5] = sum(1 for key in keys if type_components.get(key)) / length
    transitions = Counter(zip(keys, keys[1:]))
    vector[6] = len(transitions) / max(1, length - 1)
    vector[7] = len(set(type_clusters.get(key, -1) for key in keys)) / length
    for row in events:
        vector[8 + _bucket(f"B:{row.get('separator_before', '')}", 4)] += 1.0 / length
        vector[12 + _bucket(f"A:{row.get('separator_after', '')}", 4)] += 1.0 / length
        vector[16 + _bucket(f"L:{row.get('layout_role', '')}", 4)] += 1.0 / length
        vector[20 + _bucket(f"G:{type_clusters.get(_surface_key(row['visible_surface']), -1)}", 4)] += 1.0 / length
    return vector


def _architecture_stats(
    rows: Sequence[dict], type_components: dict[str, list[dict]], record_labels: dict[str, int]
) -> dict[str, float]:
    ordered = _ordered(rows)
    records = _group_records(ordered)
    n_rows = max(1, len(ordered))
    counts = Counter(_surface_key(row["visible_surface"]) for row in ordered)
    n_types = max(1, len(counts))
    entropy = -sum((count / n_rows) * _safe_log2(count / n_rows) for count in counts.values())
    repeated_fraction = sum(count for count in counts.values() if count > 1) / n_rows
    singleton_fraction = sum(count for count in counts.values() if count == 1) / n_rows
    mean_length = sum(len(row["visible_surface"]) for row in ordered) / n_rows
    record_lengths = [len(events) for events in records.values()]
    record_mean = statistics.fmean(record_lengths) if record_lengths else 1.0
    record_cv = (
        statistics.pstdev(record_lengths) / record_mean if len(record_lengths) > 1 and record_mean else 0.0
    )

    within_reuse = 0
    pair_counts: Counter[tuple[str, str]] = Counter()
    left_counts: Counter[str] = Counter()
    total_pairs = 0
    position_counts: dict[str, Counter[int]] = defaultdict(Counter)
    for events in records.values():
        seen: set[str] = set()
        length = len(events)
        for index, row in enumerate(events):
            key = _surface_key(row["visible_surface"])
            if key in seen:
                within_reuse += 1
            seen.add(key)
            position_counts[key][min(3, 4 * index // max(1, length))] += 1
        for left, right in zip(events, events[1:]):
            left_key = _surface_key(left["visible_surface"])
            right_key = _surface_key(right["visible_surface"])
            pair_counts[(left_key, right_key)] += 1
            left_counts[left_key] += 1
            total_pairs += 1
    adjacency_predictability = (
        sum(max((count for (left, _), count in pair_counts.items() if left == key), default=0) for key in left_counts)
        / max(1, total_pairs)
    )
    max_unigram = max(counts.values(), default=0) / n_rows
    position_stability = 0.0
    for key, quartiles in position_counts.items():
        count = counts[key]
        local_entropy = -sum((value / count) * _safe_log2(value / count) for value in quartiles.values())
        position_stability += (count / n_rows) * (1.0 - local_entropy / 2.0)
    morphology_rate = sum(1 for row in ordered if type_components.get(_surface_key(row["visible_surface"]))) / n_rows
    ambiguity_rate = sum(
        1 for row in ordered if str(row.get("ambiguous_boundary", "FALSE")).upper() == "TRUE"
    ) / n_rows
    schema_counts = Counter(record_labels.values())
    schema_recurrence = sum(value for value in schema_counts.values() if value > 1) / max(1, len(records))
    return {
        "n_events": float(n_rows),
        "type_token_ratio": n_types / n_rows,
        "repetition_rate": repeated_fraction,
        "singleton_event_fraction": singleton_fraction,
        "unigram_entropy": entropy,
        "normalized_entropy": entropy / max(1.0, _safe_log2(n_types)),
        "mean_group_length": mean_length,
        "record_length_variation": record_cv,
        "within_record_reuse": within_reuse / n_rows,
        "adjacency_predictability": adjacency_predictability,
        "relation_lift_proxy": max(0.0, adjacency_predictability - max_unigram),
        "position_stability": position_stability,
        "morphology_rate": morphology_rate,
        "ambiguous_boundary_rate": ambiguity_rate,
        "record_schema_recurrence": schema_recurrence,
    }


def _transition_tables(rows: Sequence[dict]) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    forward: dict[str, Counter[str]] = defaultdict(Counter)
    backward: dict[str, Counter[str]] = defaultdict(Counter)
    for events in _group_records(rows).values():
        for left, right in zip(events, events[1:]):
            left_key = _surface_key(left["visible_surface"])
            right_key = _surface_key(right["visible_surface"])
            forward[left_key][right_key] += 1
            backward[right_key][left_key] += 1
    return (
        {key: dict(sorted(counts.items())) for key, counts in sorted(forward.items())},
        {key: dict(sorted(counts.items())) for key, counts in sorted(backward.items())},
    )


def fit(train_rows: list[dict]) -> dict:
    """Fit all thresholds, vocabularies, components and centroids on train only."""

    if not train_rows:
        raise ValueError("D396S01 requires nonempty train_rows")
    worlds = {str(row["world_id"]) for row in train_rows}
    surfaces = {str(row["surface_id"]) for row in train_rows}
    seeds = {int(row["corpus_seed"]) for row in train_rows}
    if len(worlds) != 1 or len(surfaces) != 1:
        raise ValueError("fit expects one blind world and surface channel")
    # The runner supplies multiple training seeds.  Synthetic hierarchy IDs
    # are only seed-local, so namespace every physical container before
    # learning recurrence, transition, and layout summaries.
    normalized = []
    for source in train_rows:
        row = dict(source); prefix = f"{int(source['corpus_seed'])}:"
        for key in ("page_id", "paragraph_id", "record_id", "line_id"):
            row[key] = prefix + str(source[key])
        normalized.append(row)
    ordered = _ordered(normalized)
    first = ordered[0]
    world_id = next(iter(worlds))
    surface_id = next(iter(surfaces))
    corpus_seed = min(seeds)
    phase = str(first.get("phase", _phase_from_seed(corpus_seed)))
    run_id = str(first.get("run_id", f"{DECODER_ID}_{phase}_{world_id}_{corpus_seed}_{surface_id}"))

    type_features, type_counts, _, _ = _event_views(ordered)
    means, scales = _means_scales(list(type_features.values()))
    standardized = {
        key: _standardize(vector, means, scales) for key, vector in type_features.items()
    }
    graph_k = max(4, min(20, int(round(math.sqrt(len(standardized)) / 1.8))))
    graph_centroids, type_labels = _kmeans(list(standardized.items()), graph_k)
    components, type_components = _infer_components(ordered, type_labels)

    # A recurring substring is insufficient by itself: the semantics-light
    # guard can manufacture abundant accidental families.  Current productive
    # morphology is therefore licensed only when the record contexts also
    # carry stable position/transition structure.  This gate is computed from
    # observation-only training statistics and is frozen into the model.
    morphology_guard = _architecture_stats(ordered, {}, {})
    productive_context_ok = not (
        morphology_guard["position_stability"] < 0.30
        and morphology_guard["adjacency_predictability"] < 0.30
    )
    if not productive_context_ok:
        components = [
            component for component in components
            if component["status"] != "CURRENTLY_PRODUCTIVE"
        ]
        type_components = {
            key: [hit for hit in hits if hit["status"] != "CURRENTLY_PRODUCTIVE"]
            for key, hits in type_components.items()
        }

    record_vectors: dict[str, list[float]] = {}
    records = _group_records(ordered)
    for record_id, events in records.items():
        record_vectors[record_id] = _record_vector(events, type_labels, type_components)
    record_means, record_scales = _means_scales(list(record_vectors.values()))
    record_standardized = {
        key: _standardize(vector, record_means, record_scales)
        for key, vector in record_vectors.items()
    }
    record_k = max(3, min(8, int(round(math.sqrt(len(record_standardized) / 25.0)))))
    record_centroids, record_labels = _kmeans(list(record_standardized.items()), record_k)
    forward, backward = _transition_tables(ordered)

    operator_scores: dict[str, float] = {}
    record_count = max(1, len(records))
    key_records: dict[str, set[str]] = defaultdict(set)
    initial: Counter[str] = Counter()
    line_initial: Counter[str] = Counter()
    for events in records.values():
        line_seen: set[str] = set()
        for index, row in enumerate(events):
            key = _surface_key(row["visible_surface"])
            key_records[key].add(str(row["record_id"]))
            if index == 0:
                initial[key] += 1
            line_id = str(row["line_id"])
            if line_id not in line_seen:
                line_initial[key] += 1
                line_seen.add(line_id)
    for key, count in type_counts.items():
        recurrence = min(1.0, len(key_records[key]) / max(3.0, 0.10 * record_count))
        positional = max(initial[key], line_initial[key]) / count
        branching = min(1.0, len(forward.get(key, {})) / 8.0)
        operator_scores[key] = round(0.42 * recurrence + 0.38 * positional + 0.20 * branching, 8)

    architecture = _architecture_stats(ordered, type_components, record_labels)
    model = {
        "api_version": API_VERSION,
        "decoder_id": DECODER_ID,
        "world_id": world_id,
        "corpus_seed": corpus_seed,
        "surface_id": surface_id,
        "phase": phase,
        "run_id": run_id,
        "training_event_count": len(ordered),
        "training_record_count": len(records),
        "type_counts": dict(sorted(type_counts.items())),
        "graph_means": [round(value, 10) for value in means],
        "graph_scales": [round(value, 10) for value in scales],
        "graph_centroids": graph_centroids,
        "train_type_clusters": {key: int(value) for key, value in sorted(type_labels.items())},
        "components": components,
        "train_type_components": dict(sorted(type_components.items())),
        "record_means": [round(value, 10) for value in record_means],
        "record_scales": [round(value, 10) for value in record_scales],
        "record_centroids": record_centroids,
        "forward_transitions": forward,
        "backward_transitions": backward,
        "operator_scores": dict(sorted(operator_scores.items())),
        "architecture_stats": architecture,
        "fit_policy": {
            "graph_dimension": GRAPH_DIM,
            "record_dimension": RECORD_DIM,
            "component_min_types": 3,
            "component_min_records": 2,
            "target_rank_cap": MAX_TARGET_RANK,
            "morphology_rank_cap": MAX_MORPH_RANK,
            "productive_context_gate": productive_context_ok,
        },
    }
    # Fail during fit, not in the runner's post-fit hashing step, if state is unsafe.
    json.dumps(model, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return model


def _held_assignments(model: dict, rows: Sequence[dict]) -> tuple[
    dict[str, int], dict[str, tuple[float, float]], dict[str, list[dict]]
]:
    features, _, _, _ = _event_views(rows)
    type_clusters: dict[str, int] = {}
    cluster_margins: dict[str, tuple[float, float]] = {}
    for key, vector in features.items():
        if key in model["train_type_clusters"]:
            label = int(model["train_type_clusters"][key])
            standardized = _standardize(vector, model["graph_means"], model["graph_scales"])
            _, first, second = _nearest(standardized, model["graph_centroids"])
        else:
            standardized = _standardize(vector, model["graph_means"], model["graph_scales"])
            label, first, second = _nearest(standardized, model["graph_centroids"])
        type_clusters[key] = label
        cluster_margins[key] = (first, second)

    by_initial: dict[str, list[dict]] = defaultdict(list)
    for component in model["components"]:
        atoms = component["atoms"]
        if atoms:
            by_initial[_surface_key(atoms[:1])].append(component)
    type_components: dict[str, list[dict]] = defaultdict(list)
    for key in features:
        surface = _surface_from_key(key)
        for start, atom in enumerate(surface):
            for component in by_initial.get(_surface_key((atom,)), ()):
                atoms = component["atoms"]
                width = len(atoms)
                if (
                    width >= len(surface)
                    or start + width > len(surface)
                    or tuple(surface[start:start + width]) != tuple(atoms)
                ):
                    continue
                type_components[key].append(
                    {
                        "component_id": component["component_id"],
                        "start": start,
                        "end": start + width,
                        "status": component["status"],
                        "score": component["score"],
                    }
                )
        type_components[key].sort(
            key=lambda hit: (
                -float(hit["score"]),
                -(int(hit["end"]) - int(hit["start"])),
                str(hit["component_id"]),
            )
        )
        # The same component may occur twice; a ranked analysis is component-unique.
        unique: list[dict] = []
        seen: set[str] = set()
        for hit in type_components[key]:
            if str(hit["component_id"]) in seen:
                continue
            seen.add(str(hit["component_id"]))
            unique.append(hit)
        type_components[key] = unique[:MAX_MORPH_RANK]
    return type_clusters, cluster_margins, dict(type_components)


def _common(rows: Sequence[dict], representation: str, property_id: str, variant: str = "PRIMARY") -> dict:
    first = rows[0]
    seed = int(first["corpus_seed"])
    return {
        "schema_version": API_VERSION,
        "phase": str(first.get("phase", _phase_from_seed(seed))),
        "run_id": str(first.get("run_id", f"{DECODER_ID}_{seed}")),
        "world_id": str(first["world_id"]),
        "corpus_seed": seed,
        "surface_id": str(first["surface_id"]),
        "representation_id": representation,
        "decoder_id": DECODER_ID,
        "method_variant": variant,
        "property_id": property_id,
    }


def _partition_resolution(
    property_id: str,
    representation: str,
    row: dict,
    key: str,
    previous_key: str | None,
    next_key: str | None,
    type_cluster: int,
    cluster_confidence: float,
    component_hits: Sequence[dict],
) -> tuple[str, str, float]:
    lexical = _anon("C", key)
    graph = f"C_{type_cluster:03d}"
    best_current = next((hit for hit in component_hits if hit["status"] == "CURRENTLY_PRODUCTIVE"), None)
    best_fossil = next((hit for hit in component_hits if hit["status"] == "FOSSILIZED"), None)
    graph_allowed = representation in ("RECORD_TOPOLOGY", "MULTI_RESOLUTION")
    component_allowed = representation in ("INFERRED_COMPONENTS", "MULTI_RESOLUTION")

    if property_id == "LEXICAL_IDENTITY":
        return "RESOLVED", lexical, 0.99
    if property_id == "CURRENT_PRODUCTIVE_COMPONENT" and component_allowed and best_current:
        return "RESOLVED", str(best_current["component_id"]), float(best_current["score"])
    if property_id == "FOSSIL_COMPONENT" and component_allowed and best_fossil:
        return "RESOLVED", str(best_fossil["component_id"]), float(best_fossil["score"])
    if property_id == "HISTORICAL_ANCESTRY" and component_allowed and best_fossil:
        return "RESOLVED", str(best_fossil["component_id"]), float(best_fossil["score"]) * 0.85
    if property_id in ("SEMANTIC_ENTITY_IDENTITY", "SEMANTIC_CATEGORY") and graph_allowed:
        return "RESOLVED", graph, cluster_confidence
    if property_id == "CURRENT_SHARED_MEANING" and graph_allowed and component_hits:
        return "RESOLVED", graph, cluster_confidence * 0.85
    if property_id == "FUNCTION_OPERATOR_CLASS" and graph_allowed:
        position = str(row.get("line_position_bin", "")) + ":" + str(row.get("record_position_bin", ""))
        return "RESOLVED", _anon("C", f"F:{type_cluster}:{position}"), cluster_confidence * 0.90
    if property_id == "CONSTRUCTION_CLASS" and graph_allowed:
        layout = str(row.get("layout_role", ""))
        return "RESOLVED", _anon("C", f"X:{type_cluster}:{layout}"), cluster_confidence * 0.90
    if property_id == "REGISTER_REALIZATION" and graph_allowed:
        register = str(row.get("register_id", ""))
        return "RESOLVED", _anon("C", f"R:{type_cluster}:{register}"), cluster_confidence * 0.90
    if property_id == "STATE_BEFORE_IDENTITY" and graph_allowed and previous_key is not None:
        return "RESOLVED", _anon("C", f"B:{previous_key}"), 0.76
    if property_id == "STATE_AFTER_IDENTITY" and graph_allowed and next_key is not None:
        return "RESOLVED", _anon("C", f"A:{next_key}"), 0.76
    if property_id == "STATE_TRANSITION_IDENTITY" and graph_allowed and previous_key is not None and next_key is not None:
        return "RESOLVED", _anon("C", f"T:{previous_key}:{next_key}"), 0.72
    return "ABSTAIN", "", 0.0


def _target_score(
    model: dict,
    property_id: str,
    source: dict,
    target: dict,
    type_clusters: dict[str, int],
    type_components: dict[str, list[dict]],
) -> tuple[float, str]:
    source_key = _surface_key(source["visible_surface"])
    target_key = _surface_key(target["visible_surface"])
    source_rank = int(source.get("global_event_rank", source.get("event_index", 0)))
    target_rank = int(target.get("global_event_rank", target.get("event_index", 0)))
    distance = abs(source_rank - target_rank)
    same_surface = source_key == target_key
    same_cluster = type_clusters.get(source_key) == type_clusters.get(target_key)
    source_components = {hit["component_id"] for hit in type_components.get(source_key, ())}
    target_components = {hit["component_id"] for hit in type_components.get(target_key, ())}
    shared_component = bool(source_components & target_components)
    same_line = str(source["line_id"]) == str(target["line_id"])
    forward_count = int(model["forward_transitions"].get(source_key, {}).get(target_key, 0))
    backward_count = int(model["backward_transitions"].get(source_key, {}).get(target_key, 0))
    transition = min(1.0, math.log1p(forward_count + backward_count) / math.log(8.0))
    proximity = math.exp(-distance / 5.0)

    if property_id == "ENTITY_REUSE_ANTECEDENT":
        raw = 0.70 * same_surface + 0.15 * shared_component + 0.10 * same_cluster + 0.05 * proximity
        type_id = "T01" if same_surface else ("T02" if shared_component else "T03")
    elif property_id == "REFERENCE_ANAPHORA":
        raw = 0.42 * same_surface + 0.24 * shared_component + 0.16 * same_cluster + 0.18 * proximity
        type_id = "T04" if same_surface else ("T05" if shared_component else "T06")
    elif property_id == "COORDINATOR_RELATION":
        follows = target_rank > source_rank
        raw = 0.38 * proximity + 0.24 * same_line + 0.24 * transition + 0.09 * follows + 0.05 * same_cluster
        type_id = "T07" if follows else "T08"
    elif property_id == "ALTERNATIVE_RELATION":
        raw = 0.28 * proximity + 0.20 * same_line + 0.22 * transition + 0.18 * same_cluster + 0.12 * shared_component
        type_id = "T09" if target_rank > source_rank else "T10"
    else:
        raw = 0.30 * proximity + 0.18 * same_line + 0.22 * transition + 0.16 * same_cluster + 0.14 * shared_component
        type_id = "T11" if target_rank > source_rank else "T12"
    return _clip01(raw), type_id


def _candidate_pool(
    property_id: str,
    source: dict,
    records: dict[str, list[dict]],
    prior_by_surface: dict[str, list[dict]],
    prior_by_cluster: dict[int, list[dict]],
    prior_by_component: dict[str, list[dict]],
    prior_recent: Sequence[dict],
    type_clusters: dict[str, int],
    type_components: dict[str, list[dict]],
) -> list[dict]:
    if property_id in ("GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION"):
        return [row for row in records[str(source["record_id"])] if row["event_id"] != source["event_id"]]

    source_key = _surface_key(source["visible_surface"])
    pool: dict[str, dict] = {}
    for candidate in prior_by_surface.get(source_key, ())[-16:]:
        pool[str(candidate["event_id"])] = candidate
    cluster = type_clusters.get(source_key, -1)
    for candidate in prior_by_cluster.get(cluster, ())[-16:]:
        pool[str(candidate["event_id"])] = candidate
    # Recency is an observation-only fallback and bounds the all-prior universe.
    for candidate in prior_recent[-16:]:
        pool[str(candidate["event_id"])] = candidate
    source_components = {hit["component_id"] for hit in type_components.get(source_key, ())}
    for component_id in sorted(source_components):
        for candidate in prior_by_component.get(str(component_id), ())[-16:]:
            pool[str(candidate["event_id"])] = candidate
    return list(pool.values())


def decode(model: dict, held_rows: list[dict], representation: str) -> dict[str, list[dict]]:
    """Decode one held seed without changing the JSON-safe fitted model."""

    if representation not in SUPPORTED_REPRESENTATIONS:
        raise ValueError(f"D396S01 unsupported representation: {representation}")
    if not held_rows:
        return _outputs()
    if {str(row["world_id"]) for row in held_rows} != {str(model["world_id"])}:
        raise ValueError("held world does not match fitted blind world")
    if {str(row["surface_id"]) for row in held_rows} != {str(model["surface_id"])}:
        raise ValueError("held surface does not match fitted blind channel")

    outputs = _outputs()
    ordered = _ordered(held_rows)
    records = _group_records(ordered)
    type_clusters, cluster_margins, type_components = _held_assignments(model, ordered)
    record_event_lookup: dict[str, tuple[list[dict], int]] = {}
    previous_key: dict[str, str | None] = {}
    next_key: dict[str, str | None] = {}
    for events in records.values():
        for index, row in enumerate(events):
            event_id = str(row["event_id"])
            record_event_lookup[event_id] = (events, index)
            previous_key[event_id] = _surface_key(events[index - 1]["visible_surface"]) if index else None
            next_key[event_id] = _surface_key(events[index + 1]["visible_surface"]) if index + 1 < len(events) else None

    for row in ordered:
        event_id = str(row["event_id"])
        key = _surface_key(row["visible_surface"])
        cluster = type_clusters[key]
        first_distance, second_distance = cluster_margins[key]
        margin = (second_distance - first_distance) / max(1e-9, second_distance + first_distance)
        cluster_confidence = _clip01(0.55 + 0.35 * max(0.0, margin))
        hits = type_components.get(key, [])
        current_hits = [hit for hit in hits if hit["status"] == "CURRENTLY_PRODUCTIVE"]
        fossil_hits = [hit for hit in hits if hit["status"] == "FOSSILIZED"]

        for property_id in PARTITION_PROPERTIES:
            status, cluster_id, confidence = _partition_resolution(
                property_id,
                representation,
                row,
                key,
                previous_key[event_id],
                next_key[event_id],
                cluster,
                cluster_confidence,
                hits,
            )
            outputs["partition_claims"].append(
                _common(ordered, representation, property_id)
                | {
                    "unit_type": "EVENT",
                    "unit_id": event_id,
                    "claim_status": status,
                    "cluster_id": cluster_id,
                    "confidence": _clip01(confidence),
                }
            )

        operator_score = float(model["operator_scores"].get(key, 0.0))
        events, record_index = record_event_lookup[event_id]
        seen_before = any(
            _surface_key(candidate["visible_surface"]) == key for candidate in events[:record_index]
        )
        binary_values = {
            "PRODUCTIVE_MORPHOLOGY": bool(current_hits),
            "FOSSILIZED_MORPHOLOGY": bool(fossil_hits),
            "TEMPORAL_STATE_GATE": operator_score >= 0.68,
            "ENTITY_REUSE_PRESENT": seen_before,
        }
        binary_confidences = {
            "PRODUCTIVE_MORPHOLOGY": float(current_hits[0]["score"]) if current_hits else 0.74,
            "FOSSILIZED_MORPHOLOGY": float(fossil_hits[0]["score"]) if fossil_hits else 0.70,
            "TEMPORAL_STATE_GATE": operator_score if operator_score >= 0.5 else 1.0 - operator_score,
            "ENTITY_REUSE_PRESENT": 0.94 if seen_before else 0.78,
        }
        for property_id in BINARY_PROPERTIES:
            outputs["binary_claims"].append(
                _common(ordered, representation, property_id)
                | {
                    "unit_type": "EVENT",
                    "unit_id": event_id,
                    "claim_status": "RESOLVED",
                    "predicted_bool": binary_values[property_id],
                    "confidence": _clip01(binary_confidences[property_id]),
                }
            )

        if hits:
            for rank, hit in enumerate(hits[:MAX_MORPH_RANK], 1):
                outputs["morphology_claims"].append(
                    _common(ordered, representation, "MORPHOLOGY_ANALYSIS")
                    | {
                        "event_id": event_id,
                        "component_id": str(hit["component_id"]),
                        "start_offset": int(hit["start"]),
                        "end_offset": int(hit["end"]),
                        "morphology_status": str(hit["status"]),
                        "claim_status": "RESOLVED",
                        "rank": rank,
                        "confidence": _clip01(float(hit["score"])),
                    }
                )
        else:
            outputs["morphology_claims"].append(
                _common(ordered, representation, "MORPHOLOGY_ANALYSIS")
                | {
                    "event_id": event_id,
                    "component_id": "",
                    "start_offset": 0,
                    "end_offset": 0,
                    "morphology_status": "NO_COMPONENT_CLAIM",
                    "claim_status": "ABSTAIN",
                    "rank": 1,
                    "confidence": 0.0,
                }
            )

        # Structural scope is attempted only for recurrent, position-biased nodes.
        scope_common = _common(ordered, representation, "SCOPE")
        if representation in ("RECORD_TOPOLOGY", "MULTI_RESOLUTION") and operator_score >= 0.68 and len(events) > 1:
            start_index = min(record_index + 1, len(events) - 1)
            next_same = next(
                (
                    index
                    for index in range(start_index, len(events))
                    if index > record_index and _surface_key(events[index]["visible_surface"]) == key
                ),
                None,
            )
            if next_same is not None and next_same > start_index:
                end_index = next_same - 1
                scope_type = "S01"
            else:
                source_line = str(row["line_id"])
                same_line_after = [
                    index
                    for index in range(start_index, len(events))
                    if str(events[index]["line_id"]) == source_line
                ]
                end_index = max(same_line_after) if same_line_after else min(len(events) - 1, start_index + 2)
                scope_type = "S02"
            outputs["scope_claims"].append(
                scope_common
                | {
                    "source_event_id": event_id,
                    "claim_status": "RESOLVED",
                    "scope_present": True,
                    "predicted_start_event_id": str(events[start_index]["event_id"]),
                    "predicted_end_event_id": str(events[end_index]["event_id"]),
                    "scope_type_id": scope_type,
                    "confidence": _clip01(operator_score),
                }
            )
        else:
            outputs["scope_claims"].append(
                scope_common
                | {
                    "source_event_id": event_id,
                    "claim_status": "ABSTAIN",
                    "scope_present": False,
                    "predicted_start_event_id": "",
                    "predicted_end_event_id": "",
                    "scope_type_id": "",
                    "confidence": 0.0,
                }
            )

    # Record clusters use frozen training scaling and centroids.
    for record_id, events in sorted(records.items()):
        vector = _record_vector(events, type_clusters, type_components)
        standardized = _standardize(vector, model["record_means"], model["record_scales"])
        label, first_distance, second_distance = _nearest(standardized, model["record_centroids"])
        margin = (second_distance - first_distance) / max(1e-9, second_distance + first_distance)
        outputs["record_partition_claims"].append(
            _common(ordered, representation, "RECORD_SCHEMA")
            | {
                "record_id": record_id,
                "claim_status": "RESOLVED",
                "record_schema_cluster_id": f"K_{label:03d}",
                "confidence": _clip01(0.52 + 0.40 * max(0.0, margin)),
            }
        )

    prior_by_surface: dict[str, list[dict]] = defaultdict(list)
    prior_by_cluster: dict[int, list[dict]] = defaultdict(list)
    prior_by_component: dict[str, list[dict]] = defaultdict(list)
    prior_recent: list[dict] = []
    for source in ordered:
        source_id = str(source["event_id"])
        for property_id in TARGET_PROPERTIES:
            candidate_set_id = (
                "RECORD_EXCL_SELF"
                if property_id in ("GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION")
                else "PRIOR_SEED_EVENTS"
            )
            candidates = _candidate_pool(
                property_id,
                source,
                records,
                prior_by_surface,
                prior_by_cluster,
                prior_by_component,
                prior_recent,
                type_clusters,
                type_components,
            )
            scored = []
            for target in candidates:
                score, type_id = _target_score(
                    model, property_id, source, target, type_clusters, type_components
                )
                scored.append((score, str(target["event_id"]), target, type_id))
            scored.sort(key=lambda item: (-item[0], item[1]))
            selected = scored[:MAX_TARGET_RANK]
            status = "RESOLVED" if selected else "ABSTAIN"
            confidence = selected[0][0] if selected else 0.0
            outputs["target_queries"].append(
                _common(ordered, representation, property_id)
                | {
                    "source_event_id": source_id,
                    "candidate_set_id": candidate_set_id,
                    "claim_status": status,
                    "predicted_target_count": len(selected),
                    "confidence": _clip01(confidence),
                }
            )
            for rank, (score, _, target, type_id) in enumerate(selected, 1):
                outputs["target_ranks"].append(
                    _common(ordered, representation, property_id)
                    | {
                        "source_event_id": source_id,
                        "candidate_set_id": candidate_set_id,
                        "target_rank": rank,
                        "target_event_id": str(target["event_id"]),
                        "target_score": _clip01(score),
                        "type_id": type_id,
                    }
                )
        source_key = _surface_key(source["visible_surface"])
        prior_by_surface[source_key].append(source)
        prior_by_cluster[type_clusters[source_key]].append(source)
        for hit in type_components.get(source_key, ()):
            prior_by_component[str(hit["component_id"])].append(source)
        prior_recent.append(source)

    for source in classify_world(model):
        if source["representation_id"] != representation:
            continue
        row = dict(source)
        row.update({
            "phase": str(ordered[0]["phase"]), "run_id": str(ordered[0]["run_id"]),
            "world_id": str(ordered[0]["world_id"]), "corpus_seed": int(ordered[0]["corpus_seed"]),
            "surface_id": str(ordered[0]["surface_id"]), "representation_id": representation,
        })
        table = "architecture_partition_claims" if row["property_id"] == "WORLD_ARCHITECTURE" else "architecture_binary_claims"
        outputs[table].append(row)
    return outputs


def _architecture_common(model: dict, representation: str, property_id: str, variant: str) -> dict:
    return {
        "schema_version": API_VERSION,
        "phase": str(model["phase"]),
        "run_id": str(model["run_id"]),
        "world_id": str(model["world_id"]),
        "corpus_seed": int(model["corpus_seed"]),
        "surface_id": str(model["surface_id"]),
        "representation_id": representation,
        "decoder_id": DECODER_ID,
        "method_variant": variant,
        "property_id": property_id,
    }


def classify_world(model: dict) -> list[dict]:
    """Emit anonymous architecture partitions plus explicit generic flags."""

    stats = model["architecture_stats"]
    recurrent = stats["repetition_rate"] >= 0.80 and stats["singleton_event_fraction"] <= 0.30
    context_stable = stats["position_stability"] >= 0.35
    relation_signal = stats["relation_lift_proxy"] >= 0.12
    scope_or_morphology = stats["morphology_rate"] >= 0.10 or stats["position_stability"] >= 0.55
    record_signal = stats["record_schema_recurrence"] >= 0.70
    signal_count = sum((recurrent, context_stable, relation_signal, scope_or_morphology, record_signal))
    has_downstream = relation_signal or scope_or_morphology or record_signal
    structured = signal_count >= 3 and has_downstream
    semantics_light = not structured or (
        stats["position_stability"] < 0.30 and stats["adjacency_predictability"] < 0.30
    )

    primary_flags = {
        "LANGUAGE_LIKE": bool(
            stats["type_token_ratio"] >= 0.065
            and stats["normalized_entropy"] >= 0.75
            and stats["adjacency_predictability"] >= 0.28
        ),
        "NOTATION_LIKE": bool(
            stats["type_token_ratio"] < 0.10 and stats["position_stability"] >= 0.55
        ),
        "CODEBOOK_LIKE": bool(
            stats["type_token_ratio"] < 0.065 and stats["repetition_rate"] >= 0.97
        ),
        "ORGANIC_EVOLUTION_LIKE": bool(
            stats["type_token_ratio"] >= 0.07 and stats["morphology_rate"] >= 0.10
        ),
        "CLEAN_ENGINEERED_LIKE": bool(
            stats["record_schema_recurrence"] >= 0.80
            and stats["ambiguous_boundary_rate"] <= 0.30
        ),
        "SEMANTICS_LIGHT_LIKE": bool(semantics_light),
    }
    # Frozen one-dimensional comparator: mean visible group length only.
    scalar_threshold = 5.05 if model["surface_id"] == "FREE_SURFACE" else 10.10
    scalar_semantics_light = stats["mean_group_length"] >= scalar_threshold
    scalar_flags = {property_id: False for property_id in ARCHITECTURE_PROPERTIES}
    scalar_flags["SEMANTICS_LIGHT_LIKE"] = bool(scalar_semantics_light)

    architecture_signature = ":".join(
        str(value)
        for value in (
            int(stats["type_token_ratio"] >= 0.065),
            int(stats["position_stability"] >= 0.55),
            int(stats["morphology_rate"] >= 0.10),
            int(stats["record_schema_recurrence"] >= 0.80),
            int(semantics_light),
        )
    )
    rows: list[dict] = []
    for representation in SUPPORTED_REPRESENTATIONS:
        rows.append(
            _architecture_common(model, representation, "WORLD_ARCHITECTURE", "PRIMARY")
            | {
                "claim_status": "RESOLVED",
                "architecture_cluster_id": _anon("A", architecture_signature),
                "confidence": _clip01(0.52 + 0.08 * signal_count),
            }
        )
        for property_id in ARCHITECTURE_PROPERTIES:
            primary_value = primary_flags[property_id]
            primary_confidence = 0.80 if property_id == "SEMANTICS_LIGHT_LIKE" else 0.68
            rows.append(
                _architecture_common(model, representation, property_id, "PRIMARY")
                | {
                    "claim_status": "RESOLVED",
                    "predicted_bool": primary_value,
                    "confidence": primary_confidence,
                }
            )
            rows.append(
                _architecture_common(model, representation, property_id, "MULTI_CONSTRAINT")
                | {
                    "claim_status": "RESOLVED",
                    "predicted_bool": primary_value,
                    "confidence": primary_confidence,
                }
            )
            rows.append(
                _architecture_common(model, representation, property_id, "SCALAR_BOTTLENECK")
                | {
                    "claim_status": "RESOLVED",
                    "predicted_bool": scalar_flags[property_id],
                    "confidence": 0.66,
                }
            )
    return rows


def _load_allowed_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _self_validate(outputs: dict[str, list[dict]], held_rows: Sequence[dict]) -> None:
    event_rows = {str(row["event_id"]): row for row in held_rows}
    records = _group_records(held_rows)
    event_record = {
        str(row["event_id"]): str(row["record_id"])
        for row in held_rows
    }
    event_rank = {
        str(row["event_id"]): int(row.get("global_event_rank", row.get("event_index", 0)))
        for row in held_rows
    }
    for row in outputs["target_ranks"]:
        source = str(row["source_event_id"])
        target = str(row["target_event_id"])
        assert source in event_rows and target in event_rows and source != target
        if row["candidate_set_id"] == "RECORD_EXCL_SELF":
            assert event_record[source] == event_record[target]
        else:
            assert row["candidate_set_id"] == "PRIOR_SEED_EVENTS"
            assert event_rank[target] < event_rank[source]
    rank_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in outputs["target_ranks"]:
        rank_groups[(str(row["property_id"]), str(row["source_event_id"]))].append(row)
    for group in rank_groups.values():
        group.sort(key=lambda row: int(row["target_rank"]))
        assert [int(row["target_rank"]) for row in group] == list(range(1, len(group) + 1))
        scores = [float(row["target_score"]) for row in group]
        assert scores == sorted(scores, reverse=True)
    for row in outputs["scope_claims"]:
        if row["claim_status"] != "RESOLVED":
            continue
        source = str(row["source_event_id"])
        start = str(row["predicted_start_event_id"])
        end = str(row["predicted_end_event_id"])
        assert event_record[source] == event_record[start] == event_record[end]
        local = {str(item["event_id"]): int(item["record_event_ordinal"]) for item in records[event_record[source]]}
        assert local[start] <= local[end]
    for row in outputs["morphology_claims"]:
        if row["claim_status"] != "RESOLVED":
            continue
        length = len(event_rows[str(row["event_id"])]["visible_surface"])
        assert 0 <= int(row["start_offset"]) < int(row["end_offset"]) <= length


def self_test() -> int:
    """Blind smoke test: development observations only; no oracle is loaded."""

    exp = Path(__file__).resolve().parents[2]
    observation_api = _load_allowed_module(exp / "src/observation_api.py", "d396s01_observation_api")
    decoder_api = _load_allowed_module(exp / "src/decoder_api_v2.py", "d396s01_decoder_api")
    worlds = observation_api.available_worlds("development")
    seeds = observation_api.available_seeds("development")
    if not worlds or not seeds:
        raise RuntimeError("blind development observations unavailable")
    world_id = worlds[0]
    seed = seeds[0]
    summaries = []
    for surface_id in ("FREE_SURFACE", "VOYNICH_SURFACE"):
        raw_rows = observation_api.load_seed("development", world_id, seed, surface_id)
        rows = []
        for row in raw_rows:
            copied = dict(row)
            copied["phase"] = "DEVELOPMENT"
            copied["run_id"] = f"D396S01_SMOKE_{surface_id}"
            rows.append(copied)
        record_ids = sorted({str(row["record_id"]) for row in rows})
        held_records = {record_id for record_id in record_ids if _bucket(record_id, 5) == 0}
        train_rows = [row for row in rows if str(row["record_id"]) not in held_records]
        held_rows = [row for row in rows if str(row["record_id"]) in held_records]
        model = fit(train_rows)
        before = json.dumps(model, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        counts = {}
        for representation in SUPPORTED_REPRESENTATIONS:
            decoded = decode(model, held_rows, representation)
            decoder_api.validate_shape(decoded)
            _self_validate(decoded, held_rows)
            counts[representation] = {table: len(values) for table, values in decoded.items()}
        rerun = decode(model, held_rows, "MULTI_RESOLUTION")
        assert json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == json.dumps(
            decode(model, held_rows, "MULTI_RESOLUTION"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        after = json.dumps(model, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        assert before == after
        architecture_rows = classify_world(model)
        shaped = _outputs()
        for row in architecture_rows:
            table = "architecture_partition_claims" if row["property_id"] == "WORLD_ARCHITECTURE" else "architecture_binary_claims"
            shaped[table].append(row)
        decoder_api.validate_shape(shaped)
        summaries.append(
            {
                "surface": surface_id,
                "train_events": len(train_rows),
                "held_events": len(held_rows),
                "model_bytes": len(before.encode("utf-8")),
                "components": len(model["components"]),
                "graph_clusters": len(model["graph_centroids"]),
                "record_clusters": len(model["record_centroids"]),
                "multi_resolution_rows": sum(counts["MULTI_RESOLUTION"].values()),
                "architecture_rows": len(architecture_rows),
            }
        )
    print(json.dumps({"status": "PASS", "truth_scored": False, "summaries": summaries}, sort_keys=True))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the blind development-only smoke test")
    arguments = parser.parse_args()
    if not arguments.self_test:
        parser.error("no action requested; use --self-test")
    raise SystemExit(self_test())
