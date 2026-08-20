#!/usr/bin/env python3
"""D396S03: oracle-blind relation/scope topology decoder for GDT396.

Surface atoms are deliberately treated as opaque.  The decoder uses only
equality, contiguous component equality, and the visible structural metadata.
It never interprets a Unicode character or integer atom as a readable symbol.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
import hashlib
import json
import math
import statistics
from typing import Iterable


API_VERSION = 2
DECODER_ID = "D396S03"
SUPPORTED_REPRESENTATIONS = (
    "COMPOSITE_STATE",
    "CONSTRUCTION_SPAN",
    "RECORD_TOPOLOGY",
    "MULTI_RESOLUTION",
)
TARGET_PROPERTIES = (
    "GENERIC_RELATION",
    "COORDINATOR_RELATION",
    "ALTERNATIVE_RELATION",
    "REFERENCE_ANAPHORA",
    "ENTITY_REUSE_ANTECEDENT",
)

DECODER_META = {
    "api_version": API_VERSION,
    "decoder_id": DECODER_ID,
    "designer_model": "gpt-5.6-sol",
    "method_family": "RELATION_SCOPE_TOPOLOGY",
    "oracle_blind": True,
    "supported_representations": list(SUPPORTED_REPRESENTATIONS),
    "supported_claim_kinds": [
        "PARTITION", "BINARY", "RANKED_TARGET", "SCOPE", "MORPHOLOGY",
        "RECORD_SCHEMA", "WORLD_ARCHITECTURE",
    ],
    "max_rank_by_claim_kind": {
        "GENERIC_RELATION": 5,
        "COORDINATOR_RELATION": 5,
        "ALTERNATIVE_RELATION": 5,
        "REFERENCE_ANAPHORA": 5,
        "ENTITY_REUSE_ANTECEDENT": 5,
        "MORPHOLOGY_ANALYSIS": 1,
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


def _outputs() -> dict[str, list[dict]]:
    return {name: [] for name in TABLE_NAMES}


def _digest(value: object, prefix: str) -> str:
    payload = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return prefix + hashlib.blake2b(payload, digest_size=9).hexdigest()


def _atoms(surface: Iterable[object]) -> tuple[int, ...]:
    """Canonicalize without assigning meanings to the atoms."""
    out: list[int] = []
    for atom in surface:
        if isinstance(atom, int):
            out.append(atom)
        else:
            text = str(atom)
            # FREE_SURFACE is specified as a tuple of Unicode code-point
            # atoms, so this preserves one offset per visible atom.  The
            # fallback keeps the same invariant for a defensive fixture with
            # a multi-code-point element.
            if len(text) == 1:
                out.append(ord(text))
            else:
                payload = hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest()
                out.append(int.from_bytes(payload, "big") + 0x110000)
    return tuple(out)


def _surface_key(row: dict) -> str:
    return _digest(_atoms(row["visible_surface"]), "g")


def _is_unambiguous(row: dict) -> bool:
    value = row.get("ambiguous_boundary", False)
    return str(value).upper() in {"FALSE", "0", "NO", "N"}


def _entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return -sum((n / total) * math.log2(n / total) for n in counter.values())


def _mutual_information(joint: Counter, left: Counter, right: Counter) -> float:
    total = sum(joint.values())
    if not total:
        return 0.0
    value = 0.0
    for (a, b), count in joint.items():
        denom = left[a] * right[b]
        if denom:
            value += (count / total) * math.log2(count * total / denom)
    return value


def _dominant(counter: Counter, default: object = "_") -> object:
    if not counter:
        return default
    return min(counter, key=lambda key: (-counter[key], repr(key)))


def _position_bin(index: int, size: int) -> int:
    if size <= 1:
        return 0
    return min(4, (5 * index) // size)


def _record_groups(rows: list[dict]) -> list[list[dict]]:
    grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["corpus_seed"]), str(row["record_id"]))].append(row)
    result = []
    for key in sorted(grouped, key=lambda item: (item[0], item[1])):
        result.append(sorted(
            grouped[key],
            key=lambda row: (
                int(row.get("record_event_ordinal", row.get("event_index", 0))),
                int(row.get("event_index", 0)),
                str(row["event_id"]),
            ),
        ))
    return result


def _equality_shape(record: list[dict]) -> tuple[int, ...]:
    seen: dict[str, int] = {}
    shape: list[int] = []
    for row in record:
        key = _surface_key(row)
        if key not in seen:
            seen[key] = len(seen)
        shape.append(seen[key])
    return tuple(shape)


def _contains(surface: tuple[int, ...], component: tuple[int, ...]) -> list[int]:
    width = len(component)
    if not width or width > len(surface):
        return []
    return [
        index for index in range(len(surface) - width + 1)
        if surface[index:index + width] == component
    ]


def _architecture_metrics(records: list[list[dict]]) -> dict:
    rows = [row for record in records for row in record]
    token_counts = Counter(_surface_key(row) for row in rows)
    position_counts = Counter()
    token_position = Counter()
    separator_counts = Counter()
    token_separator = Counter()
    shape_counts = Counter(_equality_shape(record) for record in records)
    within_repeats = 0
    for record in records:
        observed: set[str] = set()
        for index, row in enumerate(record):
            token = _surface_key(row)
            within_repeats += int(token in observed)
            observed.add(token)
            pos = _position_bin(index, len(record))
            sep = str(row.get("separator_after", "_"))
            position_counts[pos] += 1
            token_position[(token, pos)] += 1
            separator_counts[sep] += 1
            token_separator[(token, sep)] += 1
    n_events = max(1, len(rows))
    n_records = max(1, len(records))
    ordinal_mi = _mutual_information(token_position, token_counts, position_counts)
    separator_mi = _mutual_information(token_separator, token_counts, separator_counts)
    ordinal_norm = ordinal_mi / max(1e-12, _entropy(position_counts))
    separator_norm = separator_mi / max(1e-12, _entropy(separator_counts))
    schema_recurrence = sum(
        count for count in shape_counts.values() if count >= 2
    ) / n_records
    repeat_rate = 1.0 - len(token_counts) / n_events
    signals = {
        "recurrent_partition": repeat_rate >= 0.85,
        "context_stability": ordinal_norm >= 0.20,
        "ranked_relation": schema_recurrence >= 0.55,
        "scope_or_component": separator_norm >= 0.18,
        "record_schema": schema_recurrence >= 0.55,
    }
    signal_count = sum(signals.values())
    structured = signal_count >= 3 and any(
        signals[name]
        for name in ("ranked_relation", "scope_or_component", "record_schema")
    )
    lengths = [len(record) for record in records]
    return {
        "event_count": len(rows),
        "record_count": len(records),
        "vocabulary_size": len(token_counts),
        "type_token_ratio": len(token_counts) / n_events,
        "repeat_rate": repeat_rate,
        "within_record_repeat_rate": within_repeats / n_events,
        "ordinal_mi_normalized": ordinal_norm,
        "separator_mi_normalized": separator_norm,
        "schema_recurrence": schema_recurrence,
        "record_length_cv": (
            statistics.pstdev(lengths) / max(1e-12, statistics.fmean(lengths))
            if len(lengths) > 1 else 0.0
        ),
        "signals": signals,
        "signal_count": signal_count,
        "structured_multi_constraint": structured,
        "semantics_light": not structured,
    }


def _record_coarse_features(record: list[dict]) -> list[int]:
    size = len(record)
    unique = len({_surface_key(row) for row in record})
    lines = len({str(row.get("line_id", "_")) for row in record})
    layouts = [str(row.get("layout_role", "_")) for row in record]
    separators = [str(row.get("separator_after", "_")) for row in record]
    layout_changes = sum(a != b for a, b in zip(layouts, layouts[1:]))
    sep_changes = sum(a != b for a, b in zip(separators, separators[1:]))
    repeated = size - unique
    return [
        min(12, size // 3),
        min(4, (5 * repeated) // max(1, size)),
        min(6, lines),
        min(6, layout_changes),
        min(8, sep_changes // 2),
    ]


def _role_signature(
    token: str,
    type_context: dict[str, dict[str, Counter]],
    type_atoms: dict[str, tuple[int, ...]],
    type_counts: Counter,
    n_records: int,
) -> list[object]:
    context = type_context[token]
    length = len(type_atoms[token])
    doc_bin = min(5, int(6 * context["doc_count"] / max(1, n_records)))
    count_bin = min(5, int(math.log2(1 + type_counts[token])))
    return [
        _dominant(context["position"]),
        _dominant(context["layout"]),
        _dominant(context["sep_before"]),
        _dominant(context["sep_after"]),
        min(6, length // 2),
        doc_bin,
        count_bin,
    ]


def _held_role(row: dict, index: int, size: int) -> str:
    atoms = _atoms(row["visible_surface"])
    signature = [
        _position_bin(index, size),
        str(row.get("layout_role", "_")),
        str(row.get("separator_before", "_")),
        str(row.get("separator_after", "_")),
        min(6, len(atoms) // 2),
        0,
        0,
    ]
    return _digest(signature, "c")


def _separator_boundary_scores(records: list[list[dict]]) -> dict[str, float]:
    totals: Counter = Counter()
    boundaries: Counter = Counter()
    for record in records:
        for index, row in enumerate(record):
            sep = str(row.get("separator_after", "_"))
            totals[sep] += 1
            is_boundary = index == len(record) - 1
            if not is_boundary:
                nxt = record[index + 1]
                is_boundary = (
                    str(row.get("line_id", "_")) != str(nxt.get("line_id", "_"))
                    or str(row.get("paragraph_id", "_")) != str(nxt.get("paragraph_id", "_"))
                )
            boundaries[sep] += int(is_boundary)
    return {
        sep: boundaries[sep] / totals[sep]
        for sep in sorted(totals)
    }


def _next_boundary(
    record: list[dict], index: int, boundary_scores: dict[str, float]
) -> int:
    for end in range(index, len(record)):
        row = record[end]
        if end == len(record) - 1:
            return end
        nxt = record[end + 1]
        structural_change = (
            str(row.get("line_id", "_")) != str(nxt.get("line_id", "_"))
            or str(row.get("paragraph_id", "_")) != str(nxt.get("paragraph_id", "_"))
        )
        if structural_change or boundary_scores.get(str(row.get("separator_after", "_")), 0.0) >= 0.60:
            return end
    return len(record) - 1


def _learn_components(
    records: list[list[dict]],
    type_atoms: dict[str, tuple[int, ...]],
    type_counts: Counter,
    type_docs: dict[str, set[tuple[int, str]]],
    complete_types: set[str],
    role_map: dict[str, str],
    enabled: bool,
) -> list[dict]:
    if not enabled or len(type_atoms) < 6:
        return []
    median_length = statistics.median(len(value) for value in type_atoms.values())
    min_width = max(1, min(4, round(median_length * 0.30)))
    component_types: dict[tuple[int, ...], set[str]] = defaultdict(set)
    for token in sorted(type_atoms):
        surface = type_atoms[token]
        max_width = min(len(surface) - 1, 8)
        for width in range(min_width, max_width + 1):
            for start in range(len(surface) - width + 1):
                component_types[surface[start:start + width]].add(token)

    candidates: list[tuple[float, dict]] = []
    vocab_size = len(type_atoms)
    for component, members in component_types.items():
        complete_members = members & complete_types
        if len(complete_members) < 3 or len(members) > 0.45 * vocab_size:
            continue
        docs: set[tuple[int, str]] = set()
        left_extensions: set[object] = set()
        right_extensions: set[object] = set()
        boundary_hits = 0
        total_hits = 0
        for token in members:
            docs.update(type_docs[token])
            surface = type_atoms[token]
            for start in _contains(surface, component):
                left_extensions.add(surface[start - 1] if start else None)
                end = start + len(component)
                right_extensions.add(surface[end] if end < len(surface) else None)
                boundary_hits += int(start == 0 or end == len(surface))
                total_hits += 1
        if len(docs) < 2 or len(left_extensions) < 2 or len(right_extensions) < 2:
            continue
        role_counts = Counter(role_map[token] for token in members)
        role_purity = max(role_counts.values()) / len(members)
        boundary_fraction = boundary_hits / max(1, total_hits)
        relative_width = len(component) / max(1.0, median_length)
        if role_purity >= 0.48 and boundary_fraction >= 0.45:
            status = "CURRENTLY_PRODUCTIVE"
        elif relative_width >= 0.35 and len(members) <= 32:
            status = "FOSSILIZED"
        else:
            continue
        support_score = (
            len(component) * math.log1p(len(members))
            / (1.0 + len(members) / vocab_size)
        )
        item = {
            "atoms": list(component),
            "component_id": _digest(component, "m"),
            "status": status,
            "type_support": len(members),
            "record_support": len(docs),
            "role_purity": round(role_purity, 12),
            "boundary_fraction": round(boundary_fraction, 12),
            "support_score": round(support_score, 12),
        }
        candidates.append((support_score, item))
    candidates.sort(key=lambda pair: (-pair[0], pair[1]["component_id"]))
    return [item for _, item in candidates[:512]]


def fit(train_rows: list[dict]) -> dict:
    if not train_rows:
        raise ValueError("D396S03 requires nonempty training rows")
    worlds = {str(row["world_id"]) for row in train_rows}
    surfaces = {str(row["surface_id"]) for row in train_rows}
    if len(worlds) != 1 or len(surfaces) != 1:
        raise ValueError("fit scope must contain one world and one surface channel")

    records = _record_groups(train_rows)
    rows = [row for record in records for row in record]
    type_atoms: dict[str, tuple[int, ...]] = {}
    type_counts: Counter = Counter()
    type_docs: dict[str, set[tuple[int, str]]] = defaultdict(set)
    complete_types: set[str] = set()
    type_context: dict[str, dict[str, Counter | int]] = defaultdict(
        lambda: {
            "position": Counter(), "layout": Counter(),
            "sep_before": Counter(), "sep_after": Counter(), "doc_count": 0,
        }
    )
    for record in records:
        doc = (int(record[0]["corpus_seed"]), str(record[0]["record_id"]))
        present: set[str] = set()
        for index, row in enumerate(record):
            token = _surface_key(row)
            type_atoms.setdefault(token, _atoms(row["visible_surface"]))
            type_counts[token] += 1
            type_docs[token].add(doc)
            present.add(token)
            if _is_unambiguous(row):
                complete_types.add(token)
            context = type_context[token]
            context["position"][_position_bin(index, len(record))] += 1
            context["layout"][str(row.get("layout_role", "_"))] += 1
            context["sep_before"][str(row.get("separator_before", "_"))] += 1
            context["sep_after"][str(row.get("separator_after", "_"))] += 1
        for token in present:
            type_context[token]["doc_count"] += 1

    role_map: dict[str, str] = {}
    role_signatures: dict[str, list[object]] = {}
    for token in sorted(type_atoms):
        signature = _role_signature(
            token, type_context, type_atoms, type_counts, len(records)
        )
        role_signatures[token] = signature
        role_map[token] = _digest(signature, "c")

    function_scores: dict[str, float] = {}
    for token in sorted(type_atoms):
        context = type_context[token]
        count = type_counts[token]
        docs = int(context["doc_count"])
        position_concentration = max(context["position"].values()) / count
        layout_concentration = max(context["layout"].values()) / count
        separator_concentration = max(context["sep_after"].values()) / count
        doc_fraction = docs / max(1, len(records))
        one_per_doc = min(1.0, docs / max(1, count))
        function_scores[token] = (
            math.sqrt(doc_fraction)
            * (0.40 * position_concentration
               + 0.30 * layout_concentration
               + 0.30 * separator_concentration)
            * one_per_doc
        )
    eligible = [
        token for token in type_atoms
        if type_counts[token] >= 3 and int(type_context[token]["doc_count"]) >= 2
    ]
    eligible.sort(key=lambda token: (-function_scores[token], token))
    keep_count = min(len(eligible), max(8, math.ceil(0.30 * len(eligible))))
    function_types = {
        token: round(function_scores[token], 12)
        for token in eligible[:keep_count]
    }

    architecture = _architecture_metrics(records)
    components = _learn_components(
        records, type_atoms, type_counts, type_docs, complete_types, role_map,
        enabled=bool(architecture["structured_multi_constraint"]),
    )

    equality_shapes = Counter(_digest(_equality_shape(record), "s") for record in records)
    role_shapes: Counter = Counter()
    for record in records:
        roles = tuple(role_map[_surface_key(row)] for row in record)
        signature = [list(_equality_shape(record)), list(roles)]
        role_shapes[_digest(signature, "s")] += 1
    recurrent_schemas = sorted({
        schema for schema, count in role_shapes.items() if count >= 3
    } | {
        schema for schema, count in equality_shapes.items() if count >= 3
    })

    boundary_scores = _separator_boundary_scores(records)
    scope_distributions: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        for index, row in enumerate(record[:-1]):
            token = _surface_key(row)
            end = _next_boundary(record, index + 1, boundary_scores)
            scope_distributions[token][end - index] += 1
    scope_types: dict[str, dict] = {}
    for token in sorted(function_types):
        distribution = scope_distributions.get(token, Counter())
        if not distribution:
            continue
        modal = int(_dominant(distribution, 0))
        consistency = distribution[modal] / sum(distribution.values())
        if modal >= 1 and consistency >= 0.30:
            scope_types[token] = {
                "modal_span": modal,
                "consistency": round(consistency, 12),
            }

    first = min(
        rows,
        key=lambda row: (
            int(row["corpus_seed"]), int(row.get("event_index", 0)),
            str(row["event_id"]),
        ),
    )
    model = {
        "api_version": API_VERSION,
        "decoder_id": DECODER_ID,
        "world_id": next(iter(worlds)),
        "surface_id": next(iter(surfaces)),
        "train_seeds": sorted({int(row["corpus_seed"]) for row in rows}),
        "provenance": {
            "phase": str(first.get("phase", "DEVELOPMENT")),
            "run_id": str(first.get("run_id", _digest([
                next(iter(worlds)), next(iter(surfaces)), "fit"
            ], "run"))),
            "corpus_seed": int(first["corpus_seed"]),
        },
        "type_counts": {key: int(type_counts[key]) for key in sorted(type_counts)},
        "type_doc_counts": {
            key: len(type_docs[key]) for key in sorted(type_docs)
        },
        "role_map": {key: role_map[key] for key in sorted(role_map)},
        "function_types": function_types,
        "components": components,
        "recurrent_schema_ids": recurrent_schemas,
        "boundary_scores": {
            key: round(boundary_scores[key], 12) for key in sorted(boundary_scores)
        },
        "scope_types": scope_types,
        "architecture": architecture,
        "fit_summary": {
            "events": len(rows),
            "records": len(records),
            "types": len(type_atoms),
            "roles": len(set(role_map.values())),
            "function_types": len(function_types),
            "components": len(components),
            "recurrent_schemas": len(recurrent_schemas),
        },
    }
    # Exercise canonical serialization here so a violation fails at fit time.
    json.dumps(model, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return model


def _phase_for(row: dict) -> str:
    if "phase" in row:
        return str(row["phase"])
    seed = int(row["corpus_seed"])
    if 3961000 <= seed < 3962000:
        return "QUALIFICATION"
    if seed >= 3962000:
        return "CONFIRMATION"
    return "DEVELOPMENT"


def _common(
    row: dict, representation: str, property_id: str,
    method_variant: str = "PRIMARY",
) -> dict:
    run_id = row.get("run_id")
    if run_id is None:
        run_id = _digest([
            str(row["world_id"]), int(row["corpus_seed"]),
            str(row["surface_id"]), DECODER_ID,
        ], "run")
    return {
        "schema_version": API_VERSION,
        "phase": _phase_for(row),
        "run_id": str(run_id),
        "world_id": str(row["world_id"]),
        "corpus_seed": int(row["corpus_seed"]),
        "surface_id": str(row["surface_id"]),
        "representation_id": representation,
        "decoder_id": DECODER_ID,
        "method_variant": method_variant,
        "property_id": property_id,
    }


def _component_match(model: dict, row: dict) -> dict | None:
    surface = _atoms(row["visible_surface"])
    best: tuple[float, str, int, dict] | None = None
    for component in model["components"]:
        atoms = tuple(component["atoms"])
        if len(atoms) >= len(surface):
            continue
        starts = _contains(surface, atoms)
        if not starts:
            continue
        score = (
            len(atoms) / len(surface)
            + 0.08 / math.sqrt(max(1, int(component["type_support"])))
            + 0.04 * float(component["role_purity"])
        )
        candidate = (score, str(component["component_id"]), starts[0], component)
        if best is None or candidate[:2] > best[:2]:
            best = candidate
    if best is None:
        return None
    score, _, start, component = best
    return {
        "component_id": component["component_id"],
        "status": component["status"],
        "start": start,
        "end": start + len(component["atoms"]),
        "confidence": min(0.96, max(0.52, 0.45 + 0.35 * score)),
    }


def _role_for(model: dict, row: dict, index: int, size: int) -> str:
    return model["role_map"].get(
        _surface_key(row), _held_role(row, index, size)
    )


def _schema_for(model: dict, record: list[dict], roles: list[str]) -> tuple[str, float]:
    equality = list(_equality_shape(record))
    role_schema = _digest([equality, roles], "s")
    equality_schema = _digest(equality, "s")
    recurrent = set(model["recurrent_schema_ids"])
    if role_schema in recurrent:
        return role_schema, 0.92
    if equality_schema in recurrent:
        return equality_schema, 0.84
    return _digest(_record_coarse_features(record), "s"), 0.66


def _partition_row(
    row: dict, representation: str, property_id: str, cluster_id: str,
    status: str, confidence: float,
) -> dict:
    return {
        **_common(row, representation, property_id),
        "unit_type": "EVENT",
        "unit_id": str(row["event_id"]),
        "claim_status": status,
        "cluster_id": cluster_id,
        "confidence": round(float(confidence), 12),
    }


def _binary_row(
    row: dict, representation: str, property_id: str, prediction: bool,
    status: str, confidence: float,
) -> dict:
    return {
        **_common(row, representation, property_id),
        "unit_type": "EVENT",
        "unit_id": str(row["event_id"]),
        "claim_status": status,
        "predicted_bool": bool(prediction),
        "confidence": round(float(confidence), 12),
    }


def _relation_raw_score(
    model: dict,
    source: dict,
    target: dict,
    source_index: int,
    target_index: int,
    source_role: str,
    target_role: str,
    source_component: dict | None,
    target_component: dict | None,
    property_id: str,
    record_counts: Counter,
) -> tuple[float, str]:
    same_surface = _surface_key(source) == _surface_key(target)
    same_component = bool(
        source_component and target_component
        and source_component["component_id"] == target_component["component_id"]
    )
    same_line = str(source.get("line_id", "_")) == str(target.get("line_id", "_"))
    same_layout = str(source.get("layout_role", "_")) == str(target.get("layout_role", "_"))
    distance = abs(source_index - target_index)
    target_token = _surface_key(target)
    target_function = float(model["function_types"].get(target_token, 0.0))
    source_function = float(model["function_types"].get(_surface_key(source), 0.0))
    salience = min(2, record_counts[target_token] - 1)
    score = 0.30 + 0.85 / max(1, distance)
    score += 0.45 * int(same_line) + 0.18 * int(same_layout)
    score += 0.35 * int(source_role == target_role) + 0.42 * salience
    score += 0.20 * source_function + 0.18 * max(0.0, 1.0 - target_function)
    if property_id == "GENERIC_RELATION":
        score += 2.7 * int(same_surface) + 1.5 * int(same_component)
    elif property_id == "COORDINATOR_RELATION":
        score += 1.9 * int(distance == 1) + 1.7 * int(same_component)
        score += 0.6 * int((target_index - source_index) > 0)
    elif property_id == "ALTERNATIVE_RELATION":
        score += 2.2 * int(same_component) + 1.0 * int(same_layout)
        score += 0.7 * int(distance <= 2)
    elif property_id == "REFERENCE_ANAPHORA":
        score += 3.2 * int(same_surface) + 1.8 * int(same_component)
        score += 0.8 * int(target_index < source_index)
    else:  # ENTITY_REUSE_ANTECEDENT
        score += 5.0 * int(same_surface) + 2.8 * int(same_component)
        score += 0.7 * int(source_role == target_role)
    subtype = _digest([
        int(target_index < source_index), int(same_surface),
        int(same_component), int(same_line), int(same_layout),
        min(4, distance),
    ], "t")
    return score, subtype


def _prior_candidate_pools(
    rows: list[dict], component_by_event: dict[str, dict | None]
) -> dict[str, list[dict]]:
    by_seed: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        by_seed[int(row["corpus_seed"])].append(row)
    pools: dict[str, list[dict]] = {}
    for seed in sorted(by_seed):
        ordered = sorted(by_seed[seed], key=lambda row: (
            int(row.get("event_index", row.get("global_event_rank", 0))),
            str(row["event_id"]),
        ))
        recent: deque[dict] = deque(maxlen=12)
        last_surface: dict[str, deque[dict]] = defaultdict(lambda: deque(maxlen=4))
        last_component: dict[str, deque[dict]] = defaultdict(lambda: deque(maxlen=5))
        record_prior: dict[str, deque[dict]] = defaultdict(lambda: deque(maxlen=40))
        for source in ordered:
            event_id = str(source["event_id"])
            candidates: dict[str, dict] = {}
            for target in recent:
                candidates[str(target["event_id"])] = target
            for target in last_surface.get(_surface_key(source), ()):
                candidates[str(target["event_id"])] = target
            component = component_by_event[event_id]
            if component:
                for target in last_component.get(str(component["component_id"]), ()):
                    candidates[str(target["event_id"])] = target
            for target in record_prior.get(str(source["record_id"]), ()):
                candidates[str(target["event_id"])] = target
            pools[event_id] = sorted(candidates.values(), key=lambda row: (
                int(row.get("event_index", 0)), str(row["event_id"])
            ))
            recent.append(source)
            last_surface[_surface_key(source)].append(source)
            if component:
                last_component[str(component["component_id"])].append(source)
            record_prior[str(source["record_id"])].append(source)
    return pools


def decode(model: dict, held_rows: list[dict], representation: str) -> dict[str, list[dict]]:
    if representation not in SUPPORTED_REPRESENTATIONS:
        raise ValueError(f"unsupported representation: {representation}")
    if not held_rows:
        return _outputs()
    if {str(row["world_id"]) for row in held_rows} != {str(model["world_id"])}:
        raise ValueError("held world does not match fitted world")
    if {str(row["surface_id"]) for row in held_rows} != {str(model["surface_id"])}:
        raise ValueError("held surface does not match fitted surface")

    outputs = _outputs()
    records = _record_groups(held_rows)
    all_rows = [row for record in records for row in record]
    component_by_event = {
        str(row["event_id"]): _component_match(model, row) for row in all_rows
    }
    role_by_event: dict[str, str] = {}
    schema_by_record: dict[tuple[int, str], tuple[str, float]] = {}
    record_lookup: dict[str, list[dict]] = {}
    index_by_event: dict[str, int] = {}
    for record in records:
        roles = []
        for index, row in enumerate(record):
            event_id = str(row["event_id"])
            role = _role_for(model, row, index, len(record))
            role_by_event[event_id] = role
            index_by_event[event_id] = index
            roles.append(role)
        key = (int(record[0]["corpus_seed"]), str(record[0]["record_id"]))
        schema_by_record[key] = _schema_for(model, record, roles)
        for row in record:
            record_lookup[str(row["event_id"])] = record

    # Exact equality and component/document recurrence are computed only inside
    # the held packet.  No parameter or threshold is fitted here.
    held_type_docs: dict[str, set[tuple[int, str]]] = defaultdict(set)
    for row in all_rows:
        held_type_docs[_surface_key(row)].add(
            (int(row["corpus_seed"]), str(row["record_id"]))
        )

    for record in records:
        record_key = (int(record[0]["corpus_seed"]), str(record[0]["record_id"]))
        schema_id, schema_confidence = schema_by_record[record_key]
        roles = [role_by_event[str(row["event_id"])] for row in record]
        record_counts = Counter(_surface_key(row) for row in record)
        first_occurrence: dict[str, int] = {}
        for index, row in enumerate(record):
            event_id = str(row["event_id"])
            token = _surface_key(row)
            component = component_by_event[event_id]
            role = roles[index]
            lexical_cluster = _digest(_atoms(row["visible_surface"]), "l")
            outputs["partition_claims"].append(_partition_row(
                row, representation, "LEXICAL_IDENTITY", lexical_cluster,
                "RESOLVED", 1.0,
            ))
            entity_recurrent = len(held_type_docs[token]) >= 2
            outputs["partition_claims"].append(_partition_row(
                row, representation, "SEMANTIC_ENTITY_IDENTITY",
                lexical_cluster if entity_recurrent else "z0",
                "RESOLVED" if entity_recurrent else "ABSTAIN",
                0.72 if entity_recurrent else 0.0,
            ))
            for prop, wanted_status in (
                ("CURRENT_PRODUCTIVE_COMPONENT", "CURRENTLY_PRODUCTIVE"),
                ("FOSSIL_COMPONENT", "FOSSILIZED"),
            ):
                matched = component and component["status"] == wanted_status
                outputs["partition_claims"].append(_partition_row(
                    row, representation, prop,
                    str(component["component_id"]) if matched else "z0",
                    "RESOLVED" if matched else "ABSTAIN",
                    component["confidence"] if matched else 0.0,
                ))
            if component and component["status"] == "FOSSILIZED":
                outputs["partition_claims"].append(_partition_row(
                    row, representation, "HISTORICAL_ANCESTRY",
                    str(component["component_id"]), "RESOLVED",
                    0.75 * component["confidence"],
                ))
            else:
                outputs["partition_claims"].append(_partition_row(
                    row, representation, "HISTORICAL_ANCESTRY", "z0",
                    "ABSTAIN", 0.0,
                ))
            outputs["partition_claims"].append(_partition_row(
                row, representation, "FUNCTION_OPERATOR_CLASS", role,
                "RESOLVED", 0.82 if token in model["role_map"] else 0.56,
            ))
            construction = _digest([
                schema_id, _position_bin(index, len(record)), role,
                str(row.get("layout_role", "_")),
                str(row.get("separator_after", "_")),
            ], "k")
            outputs["partition_claims"].append(_partition_row(
                row, representation, "CONSTRUCTION_CLASS", construction,
                "RESOLVED", 0.74 * schema_confidence + 0.12,
            ))
            before_role = roles[index - 1] if index else None
            after_role = roles[index + 1] if index + 1 < len(record) else None
            state_specs = (
                ("STATE_BEFORE_IDENTITY", before_role),
                ("STATE_AFTER_IDENTITY", after_role),
                ("STATE_TRANSITION_IDENTITY",
                 _digest([before_role, role, after_role], "x")
                 if before_role is not None and after_role is not None else None),
            )
            for prop, state in state_specs:
                outputs["partition_claims"].append(_partition_row(
                    row, representation, prop, str(state) if state else "z0",
                    "RESOLVED" if state else "ABSTAIN",
                    0.76 if state else 0.0,
                ))

            productive = bool(component and component["status"] == "CURRENTLY_PRODUCTIVE")
            fossil = bool(component and component["status"] == "FOSSILIZED")
            scope_info = model["scope_types"].get(token)
            gate = bool(scope_info and index + 1 < len(record))
            previous_same = token in first_occurrence
            previous_component = any(
                component and component_by_event[str(prior["event_id"])]
                and component["component_id"]
                    == component_by_event[str(prior["event_id"])] ["component_id"]
                for prior in record[:index]
            )
            for prop, prediction, confidence in (
                ("PRODUCTIVE_MORPHOLOGY", productive,
                 component["confidence"] if productive else 0.72),
                ("FOSSILIZED_MORPHOLOGY", fossil,
                 component["confidence"] if fossil else 0.72),
                ("TEMPORAL_STATE_GATE", gate,
                 (0.62 + 0.30 * float(scope_info["consistency"])) if gate else 0.66),
                ("ENTITY_REUSE_PRESENT", previous_same or previous_component,
                 0.93 if previous_same else (0.76 if previous_component else 0.70)),
            ):
                outputs["binary_claims"].append(_binary_row(
                    row, representation, prop, prediction, "RESOLVED", confidence,
                ))
            first_occurrence.setdefault(token, index)

            if component:
                outputs["morphology_claims"].append({
                    **_common(row, representation, "MORPHOLOGY_ANALYSIS"),
                    "event_id": event_id,
                    "component_id": str(component["component_id"]),
                    "start_offset": int(component["start"]),
                    "end_offset": int(component["end"]),
                    "morphology_status": str(component["status"]),
                    "claim_status": "RESOLVED",
                    "rank": 1,
                    "confidence": round(float(component["confidence"]), 12),
                })
            else:
                outputs["morphology_claims"].append({
                    **_common(row, representation, "MORPHOLOGY_ANALYSIS"),
                    "event_id": event_id,
                    "component_id": "z0",
                    "start_offset": 0,
                    "end_offset": 0,
                    "morphology_status": "NO_COMPONENT_CLAIM",
                    "claim_status": "ABSTAIN",
                    "rank": 1,
                    "confidence": 0.0,
                })

            if gate:
                desired = max(1, int(scope_info["modal_span"]))
                actual_end = _next_boundary(record, index + 1, model["boundary_scores"])
                modal_end = min(len(record) - 1, index + desired)
                # Trust a nearby observed boundary; otherwise retain the
                # training-only modal distance.
                end = actual_end if actual_end <= index + 2 * desired else modal_end
                end = max(index + 1, end)
                scope_type = _digest([
                    role,
                    str(record[end].get("separator_after", "_")),
                    min(6, end - index),
                ], "b")
                outputs["scope_claims"].append({
                    **_common(row, representation, "SCOPE"),
                    "source_event_id": event_id,
                    "claim_status": "RESOLVED",
                    "scope_present": True,
                    "predicted_start_event_id": str(record[index + 1]["event_id"]),
                    "predicted_end_event_id": str(record[end]["event_id"]),
                    "scope_type_id": scope_type,
                    "confidence": round(min(
                        0.94, 0.60 + 0.34 * float(scope_info["consistency"])
                    ), 12),
                })
            else:
                outputs["scope_claims"].append({
                    **_common(row, representation, "SCOPE"),
                    "source_event_id": event_id,
                    "claim_status": "RESOLVED",
                    "scope_present": False,
                    "predicted_start_event_id": "",
                    "predicted_end_event_id": "",
                    "scope_type_id": "z0",
                    "confidence": 0.68,
                })

        outputs["record_partition_claims"].append({
            **_common(record[0], representation, "RECORD_SCHEMA"),
            "record_id": str(record[0]["record_id"]),
            "claim_status": "RESOLVED",
            "record_schema_cluster_id": schema_id,
            "confidence": round(float(schema_confidence), 12),
        })

    # Target ranks are produced after all record-local features have been
    # frozen.  Reference pools are a bounded retrieval index over genuinely
    # prior events in the same seed; the target universe is never inferred
    # from a hidden positive anchor.
    prior_pools = _prior_candidate_pools(all_rows, component_by_event)
    for record in records:
        record_counts = Counter(_surface_key(row) for row in record)
        for source_index, source in enumerate(record):
            source_id = str(source["event_id"])
            for property_id in TARGET_PROPERTIES:
                if property_id in {
                    "GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION"
                }:
                    candidate_set_id = "RECORD_EXCL_SELF"
                    candidates = [row for row in record if row is not source]
                else:
                    candidate_set_id = "PRIOR_SEED_EVENTS"
                    candidates = prior_pools[source_id]
                ranked: list[tuple[float, str, dict]] = []
                for target in candidates:
                    target_record = record_lookup.get(str(target["event_id"]))
                    if target_record is record:
                        target_index = index_by_event[str(target["event_id"])]
                    else:
                        # A negative coordinate preserves prior direction and
                        # lets recency enter without pretending records join.
                        source_global = int(source.get("event_index", 0))
                        target_global = int(target.get("event_index", 0))
                        target_index = source_index - max(1, source_global - target_global)
                    score, subtype = _relation_raw_score(
                        model, source, target, source_index, target_index,
                        role_by_event[source_id], role_by_event[str(target["event_id"])],
                        component_by_event[source_id],
                        component_by_event[str(target["event_id"])],
                        property_id, record_counts,
                    )
                    ranked.append((score, subtype, target))
                ranked.sort(key=lambda item: (
                    -item[0], str(item[2]["event_id"])
                ))
                ranked = ranked[:DECODER_META["max_rank_by_claim_kind"][property_id]]
                status = "RESOLVED" if ranked else "ABSTAIN"
                confidence = (1.0 - math.exp(-ranked[0][0] / 5.0)) if ranked else 0.0
                outputs["target_queries"].append({
                    **_common(source, representation, property_id),
                    "source_event_id": source_id,
                    "candidate_set_id": candidate_set_id,
                    "claim_status": status,
                    "predicted_target_count": len(ranked),
                    "confidence": round(confidence, 12),
                })
                for rank, (raw_score, subtype, target) in enumerate(ranked, 1):
                    outputs["target_ranks"].append({
                        **_common(source, representation, property_id),
                        "source_event_id": source_id,
                        "candidate_set_id": candidate_set_id,
                        "target_rank": rank,
                        "target_event_id": str(target["event_id"]),
                        "target_score": round(1.0 - math.exp(-raw_score / 5.0), 12),
                        "type_id": subtype,
                    })
    return outputs


def _architecture_common(
    model: dict, property_id: str, method_variant: str
) -> dict:
    provenance = model["provenance"]
    return {
        "schema_version": API_VERSION,
        "phase": str(provenance["phase"]),
        "run_id": str(provenance["run_id"]),
        "world_id": str(model["world_id"]),
        "corpus_seed": int(provenance["corpus_seed"]),
        "surface_id": str(model["surface_id"]),
        "representation_id": "MULTI_RESOLUTION",
        "decoder_id": DECODER_ID,
        "method_variant": method_variant,
        "property_id": property_id,
    }


def classify_world(model: dict) -> list[dict]:
    """Return anonymous architecture and the frozen multi/scalar contrast."""
    metrics = model["architecture"]
    signal_vector = [
        int(metrics["signals"][name])
        for name in (
            "recurrent_partition", "context_stability", "ranked_relation",
            "scope_or_component", "record_schema",
        )
    ]
    rows: list[dict] = [{
        **_architecture_common(model, "WORLD_ARCHITECTURE", "PRIMARY"),
        "claim_status": "RESOLVED",
        "architecture_cluster_id": _digest(signal_vector, "a"),
        "confidence": round(0.55 + 0.08 * abs(metrics["signal_count"] - 2.5), 12),
    }]

    semantics_light = bool(metrics["semantics_light"])
    multi_confidence = min(0.96, 0.62 + 0.07 * abs(metrics["signal_count"] - 2.5))
    rows.append({
        **_architecture_common(model, "SEMANTICS_LIGHT_LIKE", "MULTI_CONSTRAINT"),
        "claim_status": "RESOLVED",
        "predicted_bool": semantics_light,
        "confidence": round(multi_confidence, 12),
    })
    # Development-selected scalar comparator: the type-token ratio alone.
    # Its deliberately one-dimensional band cannot consult the relation or
    # record topology used by the primary detector.
    ttr = float(metrics["type_token_ratio"])
    scalar_prediction = 0.020 <= ttr <= 0.040
    scalar_distance = min(abs(ttr - 0.020), abs(ttr - 0.040))
    rows.append({
        **_architecture_common(model, "SEMANTICS_LIGHT_LIKE", "SCALAR_BOTTLENECK"),
        "claim_status": "RESOLVED",
        "predicted_bool": scalar_prediction,
        "confidence": round(min(0.90, 0.52 + 10.0 * scalar_distance), 12),
    })
    # These generic flags are intentionally abstentions: relation topology
    # alone does not warrant readable architecture names.
    for property_id in (
        "LANGUAGE_LIKE", "NOTATION_LIKE", "CODEBOOK_LIKE",
        "ORGANIC_EVOLUTION_LIKE", "CLEAN_ENGINEERED_LIKE",
    ):
        rows.append({
            **_architecture_common(model, property_id, "PRIMARY"),
            "claim_status": "ABSTAIN",
            "predicted_bool": False,
            "confidence": 0.0,
        })
    return rows
