#!/usr/bin/env python3
"""D396S02: oracle-blind MDL/component/context decoder for GDT396.

The implementation deliberately has no imports from the experiment generator or
scorer.  Fit-time inventories, thresholds, transition counts, and centroids are
derived only from the rows supplied to ``fit``.  Decode may use the held packet
to enumerate legal candidates and equality within that packet, but never adds a
component or changes the fitted model.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
import statistics
from typing import Iterable


API_VERSION = 2
DECODER_ID = "D396S02"
REPRESENTATIONS = (
    "FULL_GROUP",
    "HOST_LIKE",
    "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN",
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

DECODER_META = {
    "api_version": API_VERSION,
    "decoder_id": DECODER_ID,
    "designer_model": "gpt-5.6-sol",
    "method_family": "MDL_COMPONENT_CONTEXT",
    "oracle_blind": True,
    "supported_representations": list(REPRESENTATIONS),
    "supported_claim_kinds": list(PARTITION_PROPERTIES)
    + list(BINARY_PROPERTIES)
    + list(TARGET_PROPERTIES)
    + ["SCOPE", "MORPHOLOGY_ANALYSIS", "RECORD_SCHEMA", "WORLD_ARCHITECTURE"]
    + list(ARCHITECTURE_PROPERTIES),
    "max_rank_by_claim_kind": {
        "GENERIC_RELATION": 5,
        "COORDINATOR_RELATION": 5,
        "ALTERNATIVE_RELATION": 5,
        "REFERENCE_ANAPHORA": 5,
        "ENTITY_REUSE_ANTECEDENT": 5,
        "MORPHOLOGY_ANALYSIS": 3,
    },
    "fit_scope": "TRAIN_ONLY_WORLD",
    "transductive_within_held_seed": True,
}

TABLE_NAMES = (
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


def _empty_outputs() -> dict[str, list[dict]]:
    return {name: [] for name in TABLE_NAMES}


def _atom_token(atom: object) -> str:
    if isinstance(atom, bool):
        return "B1" if atom else "B0"
    if isinstance(atom, int):
        return f"I{atom:08x}"
    value = str(atom)
    return "U" + value.encode("utf-8").hex()


def _tokens(row: dict) -> tuple[str, ...]:
    return tuple(_atom_token(atom) for atom in row["visible_surface"])


def _surface_key(tokens: Iterable[str]) -> str:
    # Length prefixes make this injective even for future multi-codepoint atoms.
    return "".join(f"{len(token)}:{token}" for token in tokens)


def _digest(value: object, size: int = 14) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("ascii")).hexdigest()[:size]


def _anon(kind: str, value: object) -> str:
    return f"d396s02_{kind}_{_digest(value)}"


def _pair_key(left: str, right: str) -> str:
    return _digest([left, right], 24)


def _entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return -sum((n / total) * math.log2(n / total) for n in counter.values() if n)


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _bucket(value: float, cuts: tuple[float, ...]) -> int:
    return sum(value >= cut for cut in cuts)


def _phase_from_seed(seed: int) -> str:
    if 3961000 <= seed < 3962000:
        return "QUALIFICATION"
    if seed >= 3962000:
        return "CONFIRMATION"
    return "DEVELOPMENT"


def _common(row: dict, representation: str, property_id: str, variant: str = "PRIMARY") -> dict:
    seed = int(row["corpus_seed"])
    return {
        "schema_version": API_VERSION,
        "phase": str(row.get("phase", _phase_from_seed(seed))),
        "run_id": str(row.get("run_id", f"d396s02-{seed}")),
        "world_id": str(row["world_id"]),
        "corpus_seed": seed,
        "surface_id": str(row["surface_id"]),
        "representation_id": representation,
        "decoder_id": DECODER_ID,
        "method_variant": variant,
        "property_id": property_id,
    }


def _find_subsequence(sequence: tuple[str, ...], part: tuple[str, ...]) -> list[int]:
    if not part or len(part) > len(sequence):
        return []
    return [i for i in range(len(sequence) - len(part) + 1) if sequence[i : i + len(part)] == part]


def _record_groups(rows: list[dict]) -> dict[str, list[dict]]:
    records: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        records[str(row["record_id"])].append(row)
    for record in records.values():
        record.sort(key=lambda r: (int(r.get("record_event_ordinal", 0)), int(r.get("event_index", 0))))
    return dict(records)


def _kmeans(vectors: list[list[float]], k: int, rounds: int = 18) -> list[list[float]]:
    """Small deterministic k-means used only for coarse recurrent classes."""
    if not vectors:
        return []
    k = max(1, min(k, len(vectors)))
    ordered = sorted(vectors, key=lambda v: tuple(round(x, 9) for x in v))
    if k == 1:
        picks = [ordered[len(ordered) // 2][:]]
    else:
        picks = [ordered[round(i * (len(ordered) - 1) / (k - 1))][:] for i in range(k)]
    centroids = picks
    for _ in range(rounds):
        groups: list[list[list[float]]] = [[] for _ in centroids]
        for vector in vectors:
            idx = min(range(len(centroids)), key=lambda j: (_sqdist(vector, centroids[j]), j))
            groups[idx].append(vector)
        updated = []
        for idx, group in enumerate(groups):
            if not group:
                updated.append(centroids[idx])
            else:
                updated.append([sum(row[d] for row in group) / len(group) for d in range(len(group[0]))])
        if all(_sqdist(a, b) < 1e-14 for a, b in zip(centroids, updated)):
            centroids = updated
            break
        centroids = updated
    # Canonical order prevents arbitrary class-number permutations.
    return sorted(centroids, key=lambda v: tuple(round(x, 9) for x in v))


def _sqdist(left: list[float], right: list[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right))


def _nearest(vector: list[float], centroids: list[list[float]]) -> int:
    if not centroids:
        return 0
    return min(range(len(centroids)), key=lambda j: (_sqdist(vector, centroids[j]), j))


def _surface_vector(stat: dict, mean_length: float, n_events: int, n_records: int) -> list[float]:
    return [
        min(2.0, stat["length"] / max(1.0, mean_length)) / 2.0,
        math.log1p(stat["count"]) / max(1.0, math.log1p(n_events)),
        stat["record_count"] / max(1, n_records),
        stat["mean_position"],
        stat["first_fraction"],
        stat["last_fraction"],
        min(1.0, stat["prev_entropy"] / 5.0),
        min(1.0, stat["next_entropy"] / 5.0),
        stat["repeat_fraction"],
        stat["boundary_fraction"],
    ]


def _record_vector(
    record: list[dict],
    surface_stats: dict[str, dict],
    function_keys: set[str],
    productive_sequences: list[tuple[str, ...]],
    mean_record_length: float,
    mean_surface_length: float,
) -> list[float]:
    keys = [_surface_key(_tokens(row)) for row in record]
    seqs = [_tokens(row) for row in record]
    length = len(record)
    unique_ratio = len(set(keys)) / max(1, length)
    duplicate_ratio = 1.0 - unique_ratio
    function_fraction = sum(key in function_keys for key in keys) / max(1, length)
    component_fraction = sum(
        any(len(comp) < len(seq) and _find_subsequence(seq, comp) for comp in productive_sequences)
        for seq in seqs
    ) / max(1, length)
    known_frequency = [surface_stats.get(key, {}).get("frequency", 0.0) for key in keys]
    boundary = sum(
        str(row.get("separator_before", "")) not in ("", "JOIN")
        or str(row.get("separator_after", "")) not in ("", "JOIN")
        for row in record
    ) / max(1, length)
    return [
        min(2.0, length / max(1.0, mean_record_length)) / 2.0,
        unique_ratio,
        duplicate_ratio,
        function_fraction,
        component_fraction,
        statistics.fmean(known_frequency) if known_frequency else 0.0,
        boundary,
        min(2.0, statistics.fmean(len(seq) for seq in seqs) / max(1.0, mean_surface_length)) / 2.0,
    ]


def fit(train_rows: list[dict]) -> dict:
    if not train_rows:
        raise ValueError("D396S02 requires nonempty training rows")
    worlds = {str(row["world_id"]) for row in train_rows}
    surfaces = {str(row["surface_id"]) for row in train_rows}
    seeds = {int(row["corpus_seed"]) for row in train_rows}
    if len(worlds) != 1 or len(surfaces) != 1:
        raise ValueError("fit rows must describe one world and one surface")

    # The frozen runner supplies several training seeds at once.  Record IDs
    # are world-local rather than block-global, so namespace them by seed
    # before any recurrence or transition statistic is accumulated.
    rows = []
    for source in train_rows:
        row = dict(source)
        row["record_id"] = f"{int(source['corpus_seed'])}:{source['record_id']}"
        rows.append(row)
    rows.sort(key=lambda r: (int(r["corpus_seed"]), int(r.get("event_index", 0)), str(r["event_id"])))
    records = _record_groups(rows)
    n_events = len(rows)
    n_records = len(records)
    token_rows = [_tokens(row) for row in rows]
    keys = [_surface_key(seq) for seq in token_rows]
    mean_surface_length = statistics.fmean(len(seq) for seq in token_rows)
    mean_record_length = statistics.fmean(len(record) for record in records.values())

    counts = Counter(keys)
    atom_counts = Counter(atom for seq in token_rows for atom in seq)
    record_sets: dict[str, set[str]] = defaultdict(set)
    positions: dict[str, list[float]] = defaultdict(list)
    first_counts: Counter = Counter()
    last_counts: Counter = Counter()
    boundary_counts: Counter = Counter()
    repeat_counts: Counter = Counter()
    predecessor: dict[str, Counter] = defaultdict(Counter)
    successor: dict[str, Counter] = defaultdict(Counter)
    edge_counts: Counter = Counter()
    within_record_duplicates = 0

    for record_id, record in records.items():
        record_keys = [_surface_key(_tokens(row)) for row in record]
        local = Counter(record_keys)
        within_record_duplicates += sum(max(0, count - 1) for count in local.values())
        for ordinal, (row, key) in enumerate(zip(record, record_keys)):
            record_sets[key].add(record_id)
            positions[key].append(ordinal / max(1, len(record) - 1))
            if ordinal == 0:
                first_counts[key] += 1
            if ordinal == len(record) - 1:
                last_counts[key] += 1
            if local[key] > 1:
                repeat_counts[key] += 1
            if str(row.get("separator_before", "")) not in ("", "JOIN") or str(
                row.get("separator_after", "")
            ) not in ("", "JOIN"):
                boundary_counts[key] += 1
            if ordinal:
                predecessor[key][record_keys[ordinal - 1]] += 1
                successor[record_keys[ordinal - 1]][key] += 1
                edge_counts[_pair_key(record_keys[ordinal - 1], key)] += 1

    surface_stats: dict[str, dict] = {}
    for key in sorted(counts):
        count = counts[key]
        stat = {
            "count": count,
            "frequency": count / n_events,
            "record_count": len(record_sets[key]),
            "length": next(len(seq) for seq, item_key in zip(token_rows, keys) if item_key == key),
            "mean_position": statistics.fmean(positions[key]),
            "first_fraction": first_counts[key] / count,
            "last_fraction": last_counts[key] / count,
            "boundary_fraction": boundary_counts[key] / count,
            "repeat_fraction": repeat_counts[key] / count,
            "prev_entropy": _entropy(predecessor[key]),
            "next_entropy": _entropy(successor[key]),
            "dominant_prev": (max(predecessor[key].values()) / sum(predecessor[key].values()))
            if predecessor[key]
            else 0.0,
            "dominant_next": (max(successor[key].values()) / sum(successor[key].values()))
            if successor[key]
            else 0.0,
        }
        surface_stats[key] = stat

    # Recurrent substring inventory and an explicit two-part MDL balance.
    component_raw: dict[tuple[str, ...], dict] = {}
    for row, seq, key in zip(rows, token_rows, keys):
        if len(seq) < 2:
            continue
        seen: set[tuple[str, ...]] = set()
        for width in range(1, min(6, len(seq) - 1) + 1):
            for start in range(len(seq) - width + 1):
                part = seq[start : start + width]
                if part in seen:
                    continue
                seen.add(part)
                item = component_raw.setdefault(
                    part,
                    {"event_count": 0, "types": set(), "records": set(), "left": set(), "right": set()},
                )
                item["event_count"] += 1
                item["types"].add(key)
                item["records"].add(str(row["record_id"]))
                item["left"].add(seq[start - 1] if start else "^")
                item["right"].add(seq[start + width] if start + width < len(seq) else "$")

    atom_bits = math.log2(max(2, len(atom_counts)))
    productive: list[dict] = []
    fossil: list[dict] = []
    for part, item in component_raw.items():
        type_count = len(item["types"])
        record_count = len(item["records"])
        event_count = item["event_count"]
        left_branch = len(item["left"])
        right_branch = len(item["right"])
        coverage = event_count / n_events
        width = len(part)
        savings = event_count * (max(0.55, width - 1.0) * atom_bits)
        code_cost = (width + 2.0) * atom_bits * 4.0 + type_count * 0.5
        gain = savings - code_cost
        priority = (
            1.8 * width
            + math.log2(1 + type_count)
            + 0.35 * math.log2(1 + record_count)
            + 0.20 * math.log2(1 + max(left_branch, right_branch))
            - 0.55 * math.log2(1 + event_count)
        )
        base = {
            "atoms": list(part),
            "component_id": _anon("cmp", list(part)),
            "event_count": event_count,
            "type_count": type_count,
            "record_count": record_count,
            "left_branch": left_branch,
            "right_branch": right_branch,
            "coverage": coverage,
            "mdl_gain": gain,
            "priority": priority,
        }
        if (
            type_count >= (6 if width == 1 else 3)
            and record_count >= 3
            and event_count >= 8
            and max(left_branch, right_branch) >= 3
            and coverage <= 0.45
            and gain > 0.0
        ):
            productive.append(base)
        elif (
            width >= 2
            and 2 <= type_count <= 4
            and record_count >= 3
            and event_count >= 10
            and max(left_branch, right_branch) <= 3
            and coverage <= 0.30
            and gain > 0.0
        ):
            fossil.append(base)

    productive.sort(key=lambda x: (-x["priority"], -len(x["atoms"]), x["component_id"]))
    fossil.sort(key=lambda x: (-x["priority"], -len(x["atoms"]), x["component_id"]))
    productive = productive[:384]
    productive_ids = {item["component_id"] for item in productive}
    fossil = [item for item in fossil if item["component_id"] not in productive_ids][:128]

    # Stable function-like inventory: recurrent short/boundary-bearing groups.
    function_scored = []
    for key, stat in surface_stats.items():
        if stat["record_count"] < max(3, math.ceil(0.015 * n_records)):
            continue
        shortness = max(-1.0, 1.0 - stat["length"] / max(1.0, mean_surface_length))
        score = (
            math.log2(1 + stat["record_count"])
            + 1.1 * stat["boundary_fraction"]
            + 0.8 * (stat["first_fraction"] + stat["last_fraction"])
            + 0.45 * shortness
            + 0.35 * max(stat["dominant_prev"], stat["dominant_next"])
        )
        function_scored.append((score, key))
    function_scored.sort(key=lambda pair: (-pair[0], pair[1]))
    function_cap = min(24, max(6, round(math.sqrt(len(surface_stats)))))
    function_keys = {key for _, key in function_scored[:function_cap]}

    surface_vectors = []
    surface_vector_weights = []
    for key in sorted(surface_stats):
        vector = _surface_vector(surface_stats[key], mean_surface_length, n_events, n_records)
        # A capped weight lets recurrent classes matter without allowing the most
        # common group to consume the whole partition.
        copies = min(6, 1 + round(math.log2(1 + surface_stats[key]["count"])))
        surface_vectors.extend([vector] * copies)
        surface_vector_weights.append((key, vector))
    context_centroids = _kmeans(surface_vectors, min(8, max(3, round(math.sqrt(len(surface_stats)) / 3))))
    for key, vector in surface_vector_weights:
        surface_stats[key]["context_cluster"] = _nearest(vector, context_centroids)

    productive_sequences = [tuple(item["atoms"]) for item in productive[:96]]
    record_vectors = [
        _record_vector(
            record,
            surface_stats,
            function_keys,
            productive_sequences,
            mean_record_length,
            mean_surface_length,
        )
        for record in records.values()
    ]
    record_centroids = _kmeans(record_vectors, min(6, max(3, round(math.sqrt(n_records) / 5))))

    recurrent_edge_mass = sum(count for count in edge_counts.values() if count >= 2)
    all_edge_mass = sum(edge_counts.values())
    first_ten: dict[int, Counter] = defaultdict(Counter)
    first_ten_total = 0
    for record in records.values():
        for idx, row in enumerate(record[:10]):
            first_ten[idx][_surface_key(_tokens(row))] += 1
            first_ten_total += 1
    ordinal_stability = (
        sum(max(counter.values()) for counter in first_ten.values()) / first_ten_total if first_ten_total else 0.0
    )
    component_covered = 0
    for seq in token_rows:
        if any(len(part) < len(seq) and _find_subsequence(seq, part) for part in productive_sequences):
            component_covered += 1

    type_token = len(counts) / n_events
    duplicate_fraction = within_record_duplicates / n_events
    edge_recurrence = recurrent_edge_mass / max(1, all_edge_mass)
    component_coverage = component_covered / n_events
    semantic_light_guard = (
        0.07 <= type_token <= 0.14
        and duplicate_fraction >= 0.18
        and edge_recurrence < 0.72
        and ordinal_stability < 0.11
    )
    # A no-semantics-like packet can still contain engineered repeated strings;
    # those repetitions alone are not licensed as productive morphology.
    if semantic_light_guard:
        productive = []
        fossil = []
        productive_sequences = []
        component_coverage = 0.0

    metrics = {
        "type_token_ratio": type_token,
        "repeated_type_event_fraction": sum(count for count in counts.values() if count >= 2) / n_events,
        "duplicate_fraction": duplicate_fraction,
        "edge_recurrence": edge_recurrence,
        "ordinal_stability": ordinal_stability,
        "component_coverage": component_coverage,
        "mean_surface_length": mean_surface_length,
        "mean_record_length": mean_record_length,
        "record_length_cv": statistics.pstdev([len(record) for record in records.values()])
        / max(1.0, mean_record_length),
        "semantic_light_guard": semantic_light_guard,
    }

    model = {
        "api_version": API_VERSION,
        "decoder_id": DECODER_ID,
        "method_family": "MDL_COMPONENT_CONTEXT",
        "world_id": next(iter(worlds)),
        "corpus_seed": min(seeds),
        "surface_id": next(iter(surfaces)),
        "n_events": n_events,
        "n_records": n_records,
        "mean_surface_length": mean_surface_length,
        "mean_record_length": mean_record_length,
        "surface_stats": surface_stats,
        "edge_counts": dict(edge_counts),
        "function_keys": sorted(function_keys),
        "productive_components": productive,
        "fossil_components": fossil,
        "context_centroids": context_centroids,
        "record_centroids": record_centroids,
        "metrics": metrics,
    }
    # Enforce the public API's canonical-JSON model requirement at fit time.
    json.dumps(model, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    return model


def _default_surface_stat(seq: tuple[str, ...], model: dict) -> dict:
    return {
        "count": 0,
        "frequency": 0.0,
        "record_count": 0,
        "length": len(seq),
        "mean_position": 0.5,
        "first_fraction": 0.0,
        "last_fraction": 0.0,
        "boundary_fraction": 0.0,
        "repeat_fraction": 0.0,
        "prev_entropy": 5.0,
        "next_entropy": 5.0,
        "dominant_prev": 0.0,
        "dominant_next": 0.0,
    }


def _matches(seq: tuple[str, ...], components: list[dict], proper: bool = True) -> list[dict]:
    matches = []
    for component in components:
        atoms = tuple(component["atoms"])
        if proper and len(atoms) >= len(seq):
            continue
        for start in _find_subsequence(seq, atoms):
            item = dict(component)
            item["start"] = start
            item["end"] = start + len(atoms)
            matches.append(item)
    matches.sort(
        key=lambda x: (-x["priority"], -(x["end"] - x["start"]), x["start"], x["component_id"])
    )
    return matches


def _construction_signature(seq: tuple[str, ...], matches: list[dict]) -> tuple:
    selected = []
    occupied: set[int] = set()
    for item in matches:
        span = set(range(item["start"], item["end"]))
        if span & occupied:
            continue
        selected.append(item)
        occupied |= span
        if len(selected) == 3:
            break
    coverage = len(occupied) / max(1, len(seq))
    if not selected:
        edge = "N"
    elif selected[0]["start"] == 0 and selected[0]["end"] == len(seq):
        edge = "B"
    elif selected[0]["start"] == 0:
        edge = "L"
    elif selected[0]["end"] == len(seq):
        edge = "R"
    else:
        edge = "M"
    return (
        min(3, len(selected)),
        _bucket(coverage, (0.25, 0.50, 0.75)),
        edge,
        min(4, len(seq) // 2),
    )


def _analyze_events(model: dict, rows: list[dict]) -> dict[str, dict]:
    function_keys = set(model["function_keys"])
    analyses: dict[str, dict] = {}
    for row in rows:
        seq = _tokens(row)
        key = _surface_key(seq)
        stat = model["surface_stats"].get(key)
        if stat is None:
            stat = _default_surface_stat(seq, model)
            vector = _surface_vector(stat, model["mean_surface_length"], model["n_events"], model["n_records"])
            context_cluster = _nearest(vector, model["context_centroids"])
        else:
            context_cluster = int(stat["context_cluster"])
        productive = _matches(seq, model["productive_components"])
        fossil = _matches(seq, model["fossil_components"])
        all_matches = sorted(
            productive + fossil,
            key=lambda x: (-x["priority"], -(x["end"] - x["start"]), x["component_id"]),
        )
        analyses[str(row["event_id"])] = {
            "seq": seq,
            "key": key,
            "stat": stat,
            "context_cluster": context_cluster,
            "productive": productive,
            "fossil": fossil,
            "matches": all_matches,
            "construction": _construction_signature(seq, all_matches),
            "function": key in function_keys,
        }
    return analyses


def _partition_value(
    prop: str,
    representation: str,
    event: dict,
    analysis: dict,
    previous: dict | None,
    following: dict | None,
) -> tuple[str, str, float]:
    exact = _anon("lex", analysis["key"])
    productive = analysis["productive"][0] if analysis["productive"] else None
    fossil = analysis["fossil"][0] if analysis["fossil"] else None
    context = _anon("ctx", analysis["context_cluster"])
    construction = _anon("cons", analysis["construction"])

    if prop == "LEXICAL_IDENTITY":
        confidence = 0.72 + 0.23 * (analysis["stat"]["count"] > 1)
        return "RESOLVED", exact, confidence
    if prop == "CURRENT_PRODUCTIVE_COMPONENT":
        if productive:
            return "RESOLVED", productive["component_id"], _clip(0.58 + 0.04 * math.log2(productive["type_count"]))
        return "ABSTAIN", "d396s02_none", 0.0
    if prop == "FOSSIL_COMPONENT":
        if fossil:
            return "RESOLVED", fossil["component_id"], _clip(0.55 + 0.035 * fossil["event_count"])
        return "ABSTAIN", "d396s02_none", 0.0
    if prop == "HISTORICAL_ANCESTRY":
        if fossil:
            return "RESOLVED", fossil["component_id"], 0.57
        return "ABSTAIN", "d396s02_none", 0.0
    if prop == "SEMANTIC_ENTITY_IDENTITY":
        if representation in ("HOST_LIKE", "INFERRED_COMPONENTS", "MULTI_RESOLUTION") and productive:
            return "RESOLVED", productive["component_id"], 0.63
        return "RESOLVED", exact, 0.68
    if prop == "CURRENT_SHARED_MEANING":
        # Surface recurrence alone does not license a meaning equivalence.
        return "ABSTAIN", "d396s02_none", 0.0
    if prop == "FUNCTION_OPERATOR_CLASS":
        if analysis["function"]:
            value = (analysis["context_cluster"], analysis["construction"], min(3, len(analysis["seq"])))
            return "RESOLVED", _anon("fn", value), 0.64
        return "ABSTAIN", "d396s02_none", 0.0
    if prop == "CONSTRUCTION_CLASS":
        return "RESOLVED", construction, 0.66 if analysis["matches"] else 0.56
    if prop == "REGISTER_REALIZATION":
        if productive:
            return "RESOLVED", productive["component_id"], 0.58
        return "ABSTAIN", "d396s02_none", 0.0
    if prop == "SEMANTIC_CATEGORY":
        return "RESOLVED", context, 0.58
    if prop == "STATE_BEFORE_IDENTITY":
        before = previous["context_cluster"] if previous else -1
        return "RESOLVED", _anon("bef", before), 0.57
    if prop == "STATE_AFTER_IDENTITY":
        after = following["context_cluster"] if following else -1
        return "RESOLVED", _anon("aft", after), 0.57
    if prop == "STATE_TRANSITION_IDENTITY":
        before = previous["context_cluster"] if previous else -1
        after = following["context_cluster"] if following else -1
        # Hashing a coarse 8x8 transition avoids singleton transition classes.
        return "RESOLVED", _anon("tr", [before, analysis["context_cluster"], after]), 0.56
    return "UNSUPPORTED", "d396s02_none", 0.0


def _component_overlap(left: dict, right: dict) -> float:
    left_ids = {item["component_id"] for item in left["productive"][:5]}
    right_ids = {item["component_id"] for item in right["productive"][:5]}
    if not left_ids or not right_ids:
        return 0.0
    return len(left_ids & right_ids) / len(left_ids | right_ids)


def _relation_score(
    model: dict,
    prop: str,
    source: dict,
    target: dict,
    source_analysis: dict,
    target_analysis: dict,
    same_record_distance: int | None,
) -> float:
    exact = float(source_analysis["key"] == target_analysis["key"])
    component = _component_overlap(source_analysis, target_analysis)
    edge_forward = model["edge_counts"].get(_pair_key(source_analysis["key"], target_analysis["key"]), 0)
    edge_backward = model["edge_counts"].get(_pair_key(target_analysis["key"], source_analysis["key"]), 0)
    edge = math.log1p(max(edge_forward, edge_backward)) / 5.0
    proximity = 0.0 if same_record_distance is None else 1.0 / (1.0 + abs(same_record_distance))
    prior = int(target.get("event_index", target.get("global_event_rank", 0))) < int(
        source.get("event_index", source.get("global_event_rank", 0))
    )
    if prop == "ENTITY_REUSE_ANTECEDENT":
        raw = 0.64 * exact + 0.25 * component + 0.08 * proximity + 0.03 * prior
    elif prop == "REFERENCE_ANAPHORA":
        raw = 0.38 * exact + 0.30 * component + 0.20 * proximity + 0.08 * edge + 0.04 * prior
    elif prop == "COORDINATOR_RELATION":
        after = same_record_distance is not None and same_record_distance > 0
        raw = 0.40 * proximity + 0.25 * edge + 0.18 * component + 0.12 * after + 0.05 * target_analysis["stat"]["frequency"]
    elif prop == "ALTERNATIVE_RELATION":
        raw = 0.34 * component + 0.28 * proximity + 0.22 * edge + 0.10 * (1.0 - exact) + 0.06 * prior
    else:
        raw = 0.34 * proximity + 0.30 * edge + 0.22 * component + 0.10 * exact + 0.04 * prior
    return _clip(raw)


def _architecture_predictions(model: dict) -> tuple[str, dict[str, bool], str, dict[str, bool], str]:
    m = model["metrics"]
    ttr = m["type_token_ratio"]
    edge = m["edge_recurrence"]
    duplicate = m["duplicate_fraction"]
    mean_len = m["mean_surface_length"]
    ordinal = m["ordinal_stability"]
    component = m["component_coverage"]
    sem_light = bool(m["semantic_light_guard"])

    primary_flags = {
        "LANGUAGE_LIKE": ttr >= 0.14 and mean_len >= 3.0 and duplicate < 0.12,
        "NOTATION_LIKE": edge >= 0.82 and mean_len < 3.2,
        "CODEBOOK_LIKE": ttr < 0.052 and duplicate < 0.12,
        "ORGANIC_EVOLUTION_LIKE": ttr >= 0.065 and component >= 0.18 and not sem_light,
        "CLEAN_ENGINEERED_LIKE": edge >= 0.88 and ttr < 0.06,
        "SEMANTICS_LIGHT_LIKE": sem_light,
    }
    signals = (
        m["repeated_type_event_fraction"] >= 0.80,
        edge >= 0.70,
        edge >= 0.84,
        component >= 0.18,
        ordinal >= 0.12,
    )
    multi_positive = sum(signals) >= 3 and any(signals[2:])
    multi_flags = dict(primary_flags)
    multi_flags["SEMANTICS_LIGHT_LIKE"] = sem_light or not multi_positive
    if multi_flags["SEMANTICS_LIGHT_LIKE"]:
        multi_flags["ORGANIC_EVOLUTION_LIKE"] = False

    if sem_light:
        primary_class = "SL"
    elif primary_flags["LANGUAGE_LIKE"]:
        primary_class = "LG"
    elif primary_flags["CLEAN_ENGINEERED_LIKE"]:
        primary_class = "CE"
    elif primary_flags["NOTATION_LIKE"]:
        primary_class = "NT"
    elif primary_flags["ORGANIC_EVOLUTION_LIKE"]:
        primary_class = "OE"
    else:
        primary_class = "CB"
    multi_class = "M" + "".join("1" if flag else "0" for flag in signals)
    scalar_class = "S" + str(_bucket(ttr, (0.04, 0.075, 0.12, 0.16)))
    return primary_class, primary_flags, multi_class, multi_flags, scalar_class


def _add_architecture(outputs: dict[str, list[dict]], model: dict, row: dict, representation: str) -> None:
    primary_class, primary_flags, multi_class, multi_flags, scalar_class = _architecture_predictions(model)
    for variant, cluster, confidence in (
        ("PRIMARY", primary_class, 0.68),
        ("MULTI_CONSTRAINT", multi_class, 0.72),
        ("SCALAR_BOTTLENECK", scalar_class, 0.55),
    ):
        item = _common(row, representation, "WORLD_ARCHITECTURE", variant)
        item.update(
            {
                "claim_status": "RESOLVED",
                "architecture_cluster_id": _anon("arch", [variant, cluster]),
                "confidence": confidence,
            }
        )
        outputs["architecture_partition_claims"].append(item)

    scalar_positive = model["metrics"]["type_token_ratio"] < 0.075
    for prop in ARCHITECTURE_PROPERTIES:
        for variant, prediction, confidence in (
            ("PRIMARY", primary_flags[prop], 0.67),
            ("MULTI_CONSTRAINT", multi_flags[prop], 0.71),
            ("SCALAR_BOTTLENECK", scalar_positive if prop == "CODEBOOK_LIKE" else False, 0.53),
        ):
            item = _common(row, representation, prop, variant)
            item.update({"claim_status": "RESOLVED", "predicted_bool": bool(prediction), "confidence": confidence})
            outputs["architecture_binary_claims"].append(item)


def decode(model: dict, held_rows: list[dict], representation: str) -> dict[str, list[dict]]:
    if representation not in REPRESENTATIONS:
        raise ValueError(f"D396S02 does not support {representation}")
    if not held_rows:
        return _empty_outputs()
    if model.get("api_version") != API_VERSION or model.get("decoder_id") != DECODER_ID:
        raise ValueError("incompatible D396S02 model")
    if {str(row["world_id"]) for row in held_rows} != {str(model["world_id"])}:
        raise ValueError("held rows do not match fitted world")
    if {str(row["surface_id"]) for row in held_rows} != {str(model["surface_id"])}:
        raise ValueError("held rows do not match fitted surface")

    rows = sorted(held_rows, key=lambda r: (int(r.get("event_index", 0)), str(r["event_id"])))
    outputs = _empty_outputs()
    records = _record_groups(rows)
    analyses = _analyze_events(model, rows)
    held_key_counts = Counter(analyses[str(row["event_id"])]["key"] for row in rows)

    # Event partitions and binary claims.
    for record in records.values():
        for ordinal, row in enumerate(record):
            event_id = str(row["event_id"])
            analysis = analyses[event_id]
            previous = analyses[str(record[ordinal - 1]["event_id"])] if ordinal else None
            following = analyses[str(record[ordinal + 1]["event_id"])] if ordinal + 1 < len(record) else None
            for prop in PARTITION_PROPERTIES:
                status, cluster, confidence = _partition_value(
                    prop, representation, row, analysis, previous, following
                )
                if prop == "LEXICAL_IDENTITY" and held_key_counts[analysis["key"]] > 1:
                    confidence = max(confidence, 0.94)
                claim = _common(row, representation, prop)
                claim.update(
                    {
                        "unit_type": "EVENT",
                        "unit_id": event_id,
                        "claim_status": status,
                        "cluster_id": cluster,
                        "confidence": _clip(confidence),
                    }
                )
                outputs["partition_claims"].append(claim)

            prior_record = record[:ordinal]
            prior_exact = any(analyses[str(candidate["event_id"])]["key"] == analysis["key"] for candidate in prior_record)
            prior_component = any(
                _component_overlap(analysis, analyses[str(candidate["event_id"])]) > 0 for candidate in prior_record
            )
            binary_values = {
                "PRODUCTIVE_MORPHOLOGY": bool(analysis["productive"]),
                "FOSSILIZED_MORPHOLOGY": bool(analysis["fossil"]),
                "TEMPORAL_STATE_GATE": bool(analysis["function"] and ordinal + 1 < len(record)),
                "ENTITY_REUSE_PRESENT": bool(prior_exact or prior_component),
            }
            for prop, prediction in binary_values.items():
                claim = _common(row, representation, prop)
                evidence = bool(analysis["productive"] or analysis["fossil"] or analysis["function"] or prior_exact)
                claim.update(
                    {
                        "unit_type": "EVENT",
                        "unit_id": event_id,
                        "claim_status": "RESOLVED",
                        "predicted_bool": bool(prediction),
                        "confidence": 0.72 if evidence else 0.61,
                    }
                )
                outputs["binary_claims"].append(claim)

            morph_matches = (analysis["productive"][:3] + analysis["fossil"][:3])[:3]
            if morph_matches:
                for rank, match in enumerate(morph_matches, 1):
                    status = "CURRENTLY_PRODUCTIVE" if match in analysis["productive"] else "FOSSILIZED"
                    claim = _common(row, representation, "MORPHOLOGY_ANALYSIS")
                    claim.update(
                        {
                            "event_id": event_id,
                            "component_id": match["component_id"],
                            "start_offset": int(match["start"]),
                            "end_offset": int(match["end"]),
                            "morphology_status": status,
                            "claim_status": "RESOLVED",
                            "rank": rank,
                            "confidence": _clip(0.57 + 0.045 * math.log2(1 + match["type_count"])),
                        }
                    )
                    outputs["morphology_claims"].append(claim)
            else:
                claim = _common(row, representation, "MORPHOLOGY_ANALYSIS")
                claim.update(
                    {
                        "event_id": event_id,
                        "component_id": "d396s02_none",
                        "start_offset": 0,
                        "end_offset": 0,
                        "morphology_status": "NO_COMPONENT_CLAIM",
                        "claim_status": "ABSTAIN",
                        "rank": 1,
                        "confidence": 0.0,
                    }
                )
                outputs["morphology_claims"].append(claim)

            # Gate spans are learned from recurrent source groups but clipped to
            # the visible record.  The next recurrent gate closes the span.
            scope = _common(row, representation, "SCOPE")
            if analysis["function"] and ordinal + 1 < len(record):
                start_idx = ordinal + 1
                end_idx = len(record) - 1
                for probe in range(start_idx + 1, len(record)):
                    if analyses[str(record[probe]["event_id"])]["function"]:
                        end_idx = probe - 1
                        break
                end_idx = max(start_idx, end_idx)
                scope.update(
                    {
                        "source_event_id": event_id,
                        "claim_status": "RESOLVED",
                        "scope_present": True,
                        "predicted_start_event_id": str(record[start_idx]["event_id"]),
                        "predicted_end_event_id": str(record[end_idx]["event_id"]),
                        "scope_type_id": _anon("scope", [analysis["context_cluster"], end_idx - start_idx + 1]),
                        "confidence": 0.62,
                    }
                )
            else:
                scope.update(
                    {
                        "source_event_id": event_id,
                        "claim_status": "ABSTAIN",
                        "scope_present": False,
                        "predicted_start_event_id": "",
                        "predicted_end_event_id": "",
                        "scope_type_id": "d396s02_none",
                        "confidence": 0.0,
                    }
                )
            outputs["scope_claims"].append(scope)

    # Record schemas use train-only centroids and therefore cannot singleton-fit
    # held records.
    productive_sequences = [tuple(item["atoms"]) for item in model["productive_components"][:96]]
    for record_id, record in records.items():
        vector = _record_vector(
            record,
            model["surface_stats"],
            set(model["function_keys"]),
            productive_sequences,
            model["mean_record_length"],
            model["mean_surface_length"],
        )
        cluster = _nearest(vector, model["record_centroids"])
        claim = _common(record[0], representation, "RECORD_SCHEMA")
        claim.update(
            {
                "record_id": record_id,
                "claim_status": "RESOLVED",
                "record_schema_cluster_id": _anon("record", cluster),
                "confidence": 0.61,
            }
        )
        outputs["record_partition_claims"].append(claim)

    # Ranked targets.  Relation candidates are same-record excluding self.
    # Reference candidates are earlier visible events; the same-record prior
    # subset is used because it is both conservative and licensed by that set.
    record_locations: dict[str, tuple[list[dict], int]] = {}
    for record in records.values():
        for idx, row in enumerate(record):
            record_locations[str(row["event_id"])] = (record, idx)

    for row in rows:
        event_id = str(row["event_id"])
        source_analysis = analyses[event_id]
        record, idx = record_locations[event_id]
        for prop in TARGET_PROPERTIES:
            if prop in ("REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT"):
                candidate_set_id = "PRIOR_SEED_EVENTS"
                candidates = record[:idx]
            else:
                candidate_set_id = "RECORD_EXCL_SELF"
                candidates = [candidate for candidate in record if str(candidate["event_id"]) != event_id]
            scored = []
            for candidate in candidates:
                target_id = str(candidate["event_id"])
                target_idx = record_locations[target_id][1]
                score = _relation_score(
                    model,
                    prop,
                    row,
                    candidate,
                    source_analysis,
                    analyses[target_id],
                    target_idx - idx,
                )
                scored.append((score, int(candidate.get("event_index", 0)), target_id, candidate))
            scored.sort(key=lambda item: (-item[0], -item[1], item[2]))
            scored = scored[: DECODER_META["max_rank_by_claim_kind"][prop]]
            query = _common(row, representation, prop)
            if scored:
                top = scored[0][0]
                query.update(
                    {
                        "source_event_id": event_id,
                        "candidate_set_id": candidate_set_id,
                        "claim_status": "RESOLVED",
                        "predicted_target_count": len(scored),
                        "confidence": _clip(0.50 + 0.45 * top),
                    }
                )
                outputs["target_queries"].append(query)
                for rank, (score, _, target_id, candidate) in enumerate(scored, 1):
                    target_analysis = analyses[target_id]
                    type_features = [
                        prop,
                        int(target_analysis["context_cluster"]),
                        int(source_analysis["context_cluster"]),
                        bool(source_analysis["function"]),
                    ]
                    claim = _common(row, representation, prop)
                    claim.update(
                        {
                            "source_event_id": event_id,
                            "candidate_set_id": candidate_set_id,
                            "target_rank": rank,
                            "target_event_id": target_id,
                            "target_score": _clip(score),
                            "type_id": _anon("rtype", type_features),
                        }
                    )
                    outputs["target_ranks"].append(claim)
            else:
                query.update(
                    {
                        "source_event_id": event_id,
                        "candidate_set_id": candidate_set_id,
                        "claim_status": "ABSTAIN",
                        "predicted_target_count": 0,
                        "confidence": 0.0,
                    }
                )
                outputs["target_queries"].append(query)

    _add_architecture(outputs, model, rows[0], representation)
    return outputs


def classify_world(model: dict) -> list[dict]:
    """Return normalized architecture rows using the fitted training packet.

    The main decode also emits these rows.  This standalone hook exists for API
    runners that collect architecture claims separately.
    """
    seed = int(model["corpus_seed"])
    synthetic_row = {
        "phase": _phase_from_seed(seed),
        "run_id": f"d396s02-{seed}",
        "world_id": model["world_id"],
        "corpus_seed": seed,
        "surface_id": model["surface_id"],
    }
    outputs = _empty_outputs()
    _add_architecture(outputs, model, synthetic_row, "MULTI_RESOLUTION")
    return outputs["architecture_partition_claims"] + outputs["architecture_binary_claims"]
