#!/usr/bin/env python3
"""Oracle-blind GDT396 decoder: matched conjunctive versus scalar lattice.

The implementation is intentionally self contained.  It consumes only V2
observation rows, learns only from ``fit`` rows, and emits anonymous claims.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from statistics import fmean
from typing import Iterable


API_VERSION = 2
DECODER_ID = "d396s05_multiconstraint_function"
REPRESENTATIONS = (
    "FULL_GROUP",
    "HOST_LIKE",
    "COMPOSITE_STATE",
    "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN",
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
CLUSTER_BUDGET = 8
ARCHITECTURE_CLUSTER_BUDGET = 6
RANK_CAP = 5

DECODER_META = {
    "api_version": API_VERSION,
    "decoder_id": DECODER_ID,
    "designer_model": "OpenAI Codex GPT-5 isolated context",
    "method_family": "matched_conjunctive_signal_lattice",
    "oracle_blind": True,
    "supported_representations": list(REPRESENTATIONS),
    "supported_claim_kinds": list(
        PARTITION_PROPERTIES
        + BINARY_PROPERTIES
        + TARGET_PROPERTIES
        + ("SCOPE", "MORPHOLOGY_ANALYSIS", "RECORD_SCHEMA", "WORLD_ARCHITECTURE")
        + ARCHITECTURE_PROPERTIES
    ),
    "max_rank_by_claim_kind": {**{prop: RANK_CAP for prop in TARGET_PROPERTIES}, "MORPHOLOGY_ANALYSIS": 3},
    "fit_scope": "TRAIN_ONLY_WORLD",
    "transductive_within_held_seed": True,
}


def _hid(prefix: str, *parts: object, size: int = 16) -> str:
    payload = json.dumps(parts, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return prefix + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:size]


def _surface_units(row: dict) -> tuple[str, ...]:
    raw = tuple(row.get("visible_surface", ()))
    if row.get("surface_id") == "VOYNICH_SURFACE":
        # The public channel specification fixes two transport atoms per native
        # atom.  Retaining the pairs removes the documented width artefact.
        return tuple(
            "v" + ".".join(str(int(x)) for x in raw[i : i + 2])
            for i in range(0, len(raw), 2)
        )
    return tuple("f" + str(x).encode("unicode_escape").decode("ascii") for x in raw)


def _surface_key(units: Iterable[str]) -> str:
    return json.dumps(list(units), ensure_ascii=True, separators=(",", ":"))


def _component_key(direction: str, units: tuple[str, ...]) -> str:
    return direction + ":" + _surface_key(units)


def _entropy(values: Iterable[object]) -> float:
    counts = Counter(values)
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def _modal(counter: Counter) -> tuple[str, float]:
    if not counter:
        return "NA", 0.0
    value, count = min(counter.items(), key=lambda item: (-item[1], str(item[0])))
    return str(value), count / sum(counter.values())


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(x) for x in values)
    index = q * (len(ordered) - 1)
    low = int(math.floor(index))
    high = int(math.ceil(index))
    if low == high:
        return ordered[low]
    weight = index - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def _cuts(values: list[float], bins: int) -> list[float]:
    return [_quantile(values, i / bins) for i in range(1, bins)]


def _bin(value: float, cuts: list[float]) -> int:
    # Right-open deterministic bins; duplicated cuts are harmless and preserve
    # the frozen maximum capacity without manufacturing distinctions.
    return sum(value > cut for cut in cuts)


def _cv(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = fmean(values)
    if abs(mean) < 1e-12:
        return 0.0 if max(values, default=0.0) == min(values, default=0.0) else 1.0
    return math.sqrt(fmean((x - mean) ** 2 for x in values)) / abs(mean)


def _raw_length(row: dict) -> int:
    return len(tuple(row.get("visible_surface", ())))


def _self_repeat(units: tuple[str, ...]) -> float:
    return 0.0 if not units else 1.0 - len(set(units)) / len(units)


def _phase(seed: int, row: dict) -> str:
    supplied = str(row.get("phase", ""))
    if supplied in {"DEVELOPMENT", "QUALIFICATION", "CONFIRMATION"}:
        return supplied
    if 3961000 <= seed < 3962000:
        return "QUALIFICATION"
    if seed >= 3962000:
        return "CONFIRMATION"
    return "DEVELOPMENT"


def _safe_run_id(seed: int, world: str, surface: str, row: dict) -> str:
    supplied = str(row.get("run_id", ""))
    if supplied and len(supplied) <= 128 and all(c.isalnum() or c in "_.:-" for c in supplied):
        return supplied
    return f"gdt396.{world}.{surface}.{seed}"


def _architecture_metrics(rows: list[dict]) -> dict[str, float]:
    if not rows:
        return {name: 0.0 for name in (
            "repetition_rate", "type_token_ratio", "unigram_entropy",
            "mean_group_length", "record_length_variation", "within_record_reuse",
            "boundary_stability", "component_proxy", "schema_signal",
        )}
    surfaces = [_surface_key(_surface_units(row)) for row in rows]
    counts = Counter(surfaces)
    atom_values = [unit for row in rows for unit in _surface_units(row)]
    records: dict[str, list[str]] = defaultdict(list)
    boundaries: dict[str, Counter] = defaultdict(Counter)
    lengths = []
    for row, surface in zip(rows, surfaces, strict=True):
        records[str(row["record_id"])].append(surface)
        boundaries[surface][(str(row.get("separator_before")), str(row.get("separator_after")), str(row.get("line_position_bin")))] += 1
        lengths.append(len(_surface_units(row)))
    repeated = sum(n for n in counts.values() if n > 1) / len(rows)
    within = sum(sum(n for n in Counter(seq).values() if n > 1) for seq in records.values()) / len(rows)
    boundary_stability = fmean(max(c.values()) / sum(c.values()) for c in boundaries.values())
    record_lengths = [len(seq) for seq in records.values()]
    # A strictly observation-only proxy for reusable proper pieces.
    pieces = Counter()
    piece_types: dict[str, set[str]] = defaultdict(set)
    for surface, row in zip(surfaces, rows, strict=True):
        units = _surface_units(row)
        if len(units) > 1:
            for piece in (units[:1], units[-1:]):
                key = _surface_key(piece)
                pieces[key] += 1
                piece_types[key].add(surface)
    covered_piece_events = sum(n for key, n in pieces.items() if len(piece_types[key]) >= 3)
    component_proxy = min(1.0, covered_piece_events / max(1, 2 * len(rows)))
    # Schema signal rewards reproducible record-size modes without using names.
    rc = Counter(record_lengths)
    schema_signal = max(rc.values(), default=0) / max(1, len(record_lengths))
    return {
        "repetition_rate": repeated,
        "type_token_ratio": len(counts) / len(rows),
        "unigram_entropy": _entropy(atom_values),
        "mean_group_length": fmean(lengths),
        "record_length_variation": _cv(record_lengths),
        "within_record_reuse": within,
        "boundary_stability": boundary_stability,
        "component_proxy": component_proxy,
        "schema_signal": schema_signal,
    }


def fit(train_rows: list[dict]) -> dict:
    """Fit one world/surface from one or more training seeds."""
    if not train_rows:
        raise ValueError("fit requires nonempty training rows")
    worlds = {str(row["world_id"]) for row in train_rows}
    surfaces = {str(row["surface_id"]) for row in train_rows}
    if len(worlds) != 1 or len(surfaces) != 1:
        raise ValueError("fit accepts multiple seeds but exactly one world and surface")
    world = next(iter(worlds))
    surface_id = next(iter(surfaces))
    ordered = sorted(train_rows, key=lambda r: (int(r["corpus_seed"]), int(r.get("event_index", r.get("global_event_rank", 0))), str(r["event_id"])))

    type_acc: dict[str, dict] = {}
    component_acc: dict[str, dict] = {}
    records: dict[str, list[dict]] = defaultdict(list)
    seed_rows: dict[int, list[dict]] = defaultdict(list)
    event_scalar_values: dict[str, list[float]] = defaultdict(list)
    event_scalar_seed_means: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))

    for row in ordered:
        seed = int(row["corpus_seed"])
        record_ns = f"{seed}\x1f{row['record_id']}"
        records[record_ns].append(row)
        seed_rows[seed].append(row)

    for record_ns, seq in records.items():
        seq.sort(key=lambda r: (int(r.get("record_event_ordinal", 0)), int(r.get("event_index", 0)), str(r["event_id"])))
        for i, row in enumerate(seq):
            units = _surface_units(row)
            surface = _surface_key(units)
            acc = type_acc.setdefault(surface, {
                "n": 0, "records": set(), "seeds": set(), "pre": Counter(),
                "post": Counter(), "position": Counter(), "layout": Counter(),
                "register": Counter(), "left": set(), "right": set(),
            })
            acc["n"] += 1
            acc["records"].add(record_ns)
            acc["seeds"].add(int(row["corpus_seed"]))
            acc["pre"][str(row.get("separator_before", "NA"))] += 1
            acc["post"][str(row.get("separator_after", "NA"))] += 1
            acc["position"][str(row.get("line_position_bin", "NA"))] += 1
            acc["layout"][str(row.get("layout_role", "NA"))] += 1
            acc["register"][str(row.get("register_id", "NA"))] += 1
            if i:
                acc["left"].add(_surface_key(_surface_units(seq[i - 1])))
            if i + 1 < len(seq):
                acc["right"].add(_surface_key(_surface_units(seq[i + 1])))
            if len(units) > 1:
                max_width = min(3, len(units) - 1)
                for width in range(1, max_width + 1):
                    for direction, piece in (("P", units[:width]), ("S", units[-width:])):
                        key = _component_key(direction, piece)
                        comp = component_acc.setdefault(key, {
                            "n": 0, "types": set(), "records": set(), "seeds": set(),
                            "positions": Counter(), "width": width,
                        })
                        comp["n"] += 1
                        comp["types"].add(surface)
                        comp["records"].add(record_ns)
                        comp["seeds"].add(int(row["corpus_seed"]))
                        comp["positions"][str(row.get("line_position_bin", "NA"))] += 1

    # Freeze reusable proper pieces.  Productive pieces cross at least three
    # complete types, two records and (when available) two training seeds.
    components = {}
    seed_requirement = min(2, len(seed_rows))
    for key, acc in component_acc.items():
        type_support = len(acc["types"])
        record_support = len(acc["records"])
        seed_support = len(acc["seeds"])
        if type_support >= 3 and record_support >= 2 and seed_support >= seed_requirement:
            status = "CURRENTLY_PRODUCTIVE"
        elif acc["n"] >= 3 and record_support >= 2 and type_support >= 2:
            status = "FOSSILIZED"
        else:
            continue
        modal_position = max(acc["positions"].values()) / sum(acc["positions"].values())
        support = min(1.0, math.log1p(acc["n"]) / 6.0) * (0.55 + 0.45 * (1.0 - modal_position))
        components[key] = {
            "id": _hid("cmp_", key),
            "status": status,
            "count": int(acc["n"]),
            "type_support": type_support,
            "record_support": record_support,
            "seed_support": seed_support,
            "width": int(acc["width"]),
            "confidence": round(min(0.99, max(0.05, support)), 8),
        }

    types = {}
    max_count = max((acc["n"] for acc in type_acc.values()), default=1)
    for surface, acc in type_acc.items():
        units = tuple(json.loads(surface))
        candidates = []
        if len(units) > 1:
            for width in range(1, min(3, len(units) - 1) + 1):
                for direction, piece in (("P", units[:width]), ("S", units[-width:])):
                    key = _component_key(direction, piece)
                    if key in components:
                        comp = components[key]
                        score = (2 if comp["status"] == "CURRENTLY_PRODUCTIVE" else 1, width, comp["type_support"], comp["count"], key)
                        candidates.append((score, key))
        component = max(candidates)[1] if candidates else ""
        pre, pre_p = _modal(acc["pre"])
        post, post_p = _modal(acc["post"])
        position, position_p = _modal(acc["position"])
        layout, layout_p = _modal(acc["layout"])
        register, register_p = _modal(acc["register"])
        types[surface] = {
            "count": int(acc["n"]),
            "record_support": len(acc["records"]),
            "seed_support": len(acc["seeds"]),
            "frequency_score": round(math.log1p(acc["n"]) / math.log1p(max_count), 8),
            "pre_mode": pre, "pre_stability": round(pre_p, 8),
            "post_mode": post, "post_stability": round(post_p, 8),
            "position_mode": position, "position_stability": round(position_p, 8),
            "layout_mode": layout, "layout_stability": round(layout_p, 8),
            "register_mode": register, "register_stability": round(register_p, 8),
            "left_degree": len(acc["left"]), "right_degree": len(acc["right"]),
            "component": component,
        }

    # Event scalar selection is unsupervised and train-only.  It rewards
    # non-degenerate spread and penalizes between-seed drift.  Only the winning
    # statistic and its cuts are subsequently visible to the scalar route.
    for row in ordered:
        seed = int(row["corpus_seed"])
        units = _surface_units(row)
        surface = _surface_key(units)
        info = types[surface]
        values = {
            "group_length": float(len(units)),
            "training_recurrence": math.log1p(info["count"]),
            "within_group_repetition": _self_repeat(units),
            "within_group_entropy": _entropy(units),
            "boundary_concentration": fmean((info["pre_stability"], info["post_stability"], info["position_stability"])),
        }
        for name, value in values.items():
            event_scalar_values[name].append(value)
            event_scalar_seed_means[name][seed].append(value)
    scalar_scores = {}
    for name, values in event_scalar_values.items():
        q10, q90 = _quantile(values, 0.1), _quantile(values, 0.9)
        spread = q90 - q10
        seed_means = [fmean(v) for _, v in sorted(event_scalar_seed_means[name].items())]
        drift = _cv(seed_means)
        scalar_scores[name] = spread / (1.0 + drift)
    event_scalar_name = min(scalar_scores, key=lambda name: (-scalar_scores[name], name))

    seed_namespaces = {}
    architecture_by_seed = {}
    for seed, rows in sorted(seed_rows.items()):
        metrics = _architecture_metrics(rows)
        architecture_by_seed[str(seed)] = {key: round(value, 10) for key, value in metrics.items()}
        seed_records = {str(row["record_id"]) for row in rows}
        seed_types = {_surface_key(_surface_units(row)) for row in rows}
        seed_namespaces[str(seed)] = {
            "event_count": len(rows),
            "record_count": len(seed_records),
            "surface_type_count": len(seed_types),
            "namespace_digest": _hid("ns_", world, surface_id, seed),
        }

    arch_scalar_candidates = (
        "repetition_rate", "type_token_ratio", "unigram_entropy",
        "mean_group_length", "record_length_variation",
    )
    # Choose the most stable nonconstant architecture scalar across training
    # seeds.  This uses no labels and is frozen in the returned model.
    arch_choice_scores = {}
    for name in arch_scalar_candidates:
        vals = [architecture_by_seed[str(seed)][name] for seed in sorted(seed_rows)]
        nonconstant = abs(_quantile(vals, 0.9) - _quantile(vals, 0.1)) + abs(fmean(vals)) * 1e-6
        arch_choice_scores[name] = nonconstant / (1.0 + _cv(vals))
    architecture_scalar_name = min(arch_choice_scores, key=lambda name: (-arch_choice_scores[name], name))
    architecture_scalar_values = [architecture_by_seed[str(seed)][architecture_scalar_name] for seed in sorted(seed_rows)]

    record_lengths = [len(seq) for seq in records.values()]
    model = {
        "api_version": API_VERSION,
        "decoder_id": DECODER_ID,
        "world_id": world,
        "surface_id": surface_id,
        "training_seeds": sorted(seed_rows),
        "seed_namespaces": seed_namespaces,
        "training_event_count": len(ordered),
        "types": types,
        "components": components,
        "event_scalar": {
            "name": event_scalar_name,
            "cuts": [round(x, 10) for x in _cuts(event_scalar_values[event_scalar_name], CLUSTER_BUDGET)],
            "selection_scores": {key: round(value, 10) for key, value in sorted(scalar_scores.items())},
        },
        "architecture": {
            "by_seed": architecture_by_seed,
            "means": {
                name: round(fmean(metrics[name] for metrics in architecture_by_seed.values()), 10)
                for name in next(iter(architecture_by_seed.values()))
            },
            "scalar_name": architecture_scalar_name,
            "scalar_cuts": [round(x, 10) for x in _cuts(architecture_scalar_values, ARCHITECTURE_CLUSTER_BUDGET)],
            "selection_scores": {key: round(value, 10) for key, value in sorted(arch_choice_scores.items())},
        },
        "record_length_cuts": [round(x, 10) for x in _cuts([float(x) for x in record_lengths], 6)],
        "cluster_budget": CLUSTER_BUDGET,
        "architecture_cluster_budget": ARCHITECTURE_CLUSTER_BUDGET,
    }
    # Mechanical guarantee for the runner's canonical-JSON model contract.
    json.dumps(model, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return model


def _best_component(model: dict, units: tuple[str, ...]) -> tuple[str, dict | None, int, int]:
    candidates = []
    if len(units) > 1:
        for width in range(1, min(3, len(units) - 1) + 1):
            for direction, piece, start, end in (
                ("P", units[:width], 0, width),
                ("S", units[-width:], len(units) - width, len(units)),
            ):
                key = _component_key(direction, piece)
                info = model["components"].get(key)
                if info:
                    score = (2 if info["status"] == "CURRENTLY_PRODUCTIVE" else 1, width, info["type_support"], info["count"], key)
                    candidates.append((score, key, info, start, end))
    if not candidates:
        return "", None, 0, 0
    _, key, info, start, end = max(candidates)
    return key, info, start, end


def _event_scalar(model: dict, units: tuple[str, ...], type_info: dict | None) -> float:
    name = model["event_scalar"]["name"]
    info = type_info or {}
    values = {
        "group_length": float(len(units)),
        "training_recurrence": math.log1p(float(info.get("count", 0))),
        "within_group_repetition": _self_repeat(units),
        "within_group_entropy": _entropy(units),
        "boundary_concentration": fmean((
            float(info.get("pre_stability", 0.0)),
            float(info.get("post_stability", 0.0)),
            float(info.get("position_stability", 0.0)),
        )),
    }
    return values[name]


def _signals(model: dict, item: dict) -> tuple[int, int, int, int]:
    info = item["type_info"] or {}
    recurrence = min(3, int(math.log2(1 + int(info.get("count", 0)))))
    agreements = sum((
        str(item["row"].get("separator_before", "NA")) == info.get("pre_mode"),
        str(item["row"].get("separator_after", "NA")) == info.get("post_mode"),
        str(item["row"].get("line_position_bin", "NA")) == info.get("position_mode"),
    ))
    boundary = int(agreements >= 2) + int(agreements == 3)
    known_neighbors = int(bool(item.get("prev_info"))) + int(bool(item.get("next_info")))
    compatible = int(item.get("prev_component") == item["component"] and bool(item["component"])) + int(item.get("next_component") == item["component"] and bool(item["component"]))
    context = min(2, known_neighbors + compatible)
    comp_info = item["component_info"]
    construction = 0 if not comp_info else (2 if comp_info["status"] == "CURRENTLY_PRODUCTIVE" else 1)
    return recurrence, boundary, context, construction


def _confidence(known: bool, *signals: float) -> float:
    base = 0.52 if known else 0.35
    if signals:
        base += 0.35 * min(1.0, max(0.0, fmean(float(x) for x in signals)))
    return round(min(0.99, max(0.01, base)), 8)


def _common(row: dict, representation: str, method: str, prop: str) -> dict:
    seed = int(row["corpus_seed"])
    world = str(row["world_id"])
    surface = str(row["surface_id"])
    return {
        "schema_version": API_VERSION,
        "phase": _phase(seed, row),
        "run_id": _safe_run_id(seed, world, surface, row),
        "world_id": world,
        "corpus_seed": seed,
        "surface_id": surface,
        "representation_id": representation,
        "decoder_id": DECODER_ID,
        "method_variant": method,
        "property_id": prop,
    }


def _partition_value(prop: str, item: dict, representation: str) -> tuple[bool, str, float]:
    surface = item["surface"]
    info = item["type_info"]
    component = item["component"]
    comp_info = item["component_info"]
    row = item["row"]
    known = info is not None
    boundary = (str(row.get("separator_before", "NA")), str(row.get("separator_after", "NA")), str(row.get("line_position_bin", "NA")))
    core = component or surface
    historical = (len(item["units"]), item["units"][:1], item["units"][-1:])
    behavior = (
        info.get("position_mode", "NA") if info else str(row.get("line_position_bin", "NA")),
        info.get("pre_mode", "NA") if info else str(row.get("separator_before", "NA")),
        info.get("post_mode", "NA") if info else str(row.get("separator_after", "NA")),
        min(3, int(math.log2(1 + int(info.get("count", 0))))) if info else 0,
    )
    if prop == "LEXICAL_IDENTITY":
        return True, _hid("p_", prop, surface), _confidence(known, float(info.get("frequency_score", 0.0)) if info else 0.0)
    if prop == "SEMANTIC_ENTITY_IDENTITY":
        return bool(known and (component or info["count"] >= 2)), _hid("p_", prop, core), _confidence(known, 0.7 if component else 0.3)
    if prop == "HISTORICAL_ANCESTRY":
        return len(item["units"]) > 1, _hid("p_", prop, historical), _confidence(known, 0.6 if component else 0.35)
    if prop == "CURRENT_PRODUCTIVE_COMPONENT":
        ok = bool(comp_info and comp_info["status"] == "CURRENTLY_PRODUCTIVE")
        return ok, _hid("p_", prop, component), float(comp_info["confidence"] if ok else 0.0)
    if prop == "FOSSIL_COMPONENT":
        ok = bool(comp_info and comp_info["status"] == "FOSSILIZED")
        return ok, _hid("p_", prop, component), float(comp_info["confidence"] if ok else 0.0)
    if prop == "CURRENT_SHARED_MEANING":
        return known, _hid("p_", prop, behavior), _confidence(known, 0.55)
    if prop == "FUNCTION_OPERATOR_CLASS":
        key = {
            "FULL_GROUP": surface,
            "HOST_LIKE": core,
            "COMPOSITE_STATE": (surface, boundary),
            "INFERRED_COMPONENTS": component or historical,
            "CONSTRUCTION_SPAN": (component or historical, boundary),
            "RECORD_TOPOLOGY": (item["record_length_bin"], item["ordinal_bin"], item["prior_exact"] > 0),
            "MULTI_RESOLUTION": _signals(item["model"], item),
        }[representation]
        return True, _hid("p_", prop, representation, key), _confidence(known, 0.65)
    if prop == "CONSTRUCTION_CLASS":
        return bool(component), _hid("p_", prop, component, boundary), _confidence(known, 0.75 if component else 0.0)
    if prop == "REGISTER_REALIZATION":
        return known, _hid("p_", prop, core, str(row.get("register_id", "NA"))), _confidence(known, float(info.get("register_stability", 0.0)) if info else 0.0)
    if prop == "SEMANTIC_CATEGORY":
        return known, _hid("p_", prop, behavior, item["prev_component"], item["next_component"]), _confidence(known, 0.5)
    if prop == "STATE_BEFORE_IDENTITY":
        return True, _hid("p_", prop, item["prev_component"] or item["prev_surface"] or "START"), _confidence(bool(item["prev_surface"]), 0.55)
    if prop == "STATE_AFTER_IDENTITY":
        return True, _hid("p_", prop, item["next_component"] or item["next_surface"] or "END"), _confidence(bool(item["next_surface"]), 0.55)
    if prop == "STATE_TRANSITION_IDENTITY":
        return True, _hid("p_", prop, item["prev_component"] or "START", item["next_component"] or "END"), _confidence(known, 0.6)
    raise ValueError(prop)


def _similarity(a: dict, b: dict) -> tuple[float, float, float]:
    exact = float(a["surface"] == b["surface"])
    component = float(bool(a["component"]) and a["component"] == b["component"])
    aset, bset = set(a["units"]), set(b["units"])
    overlap = len(aset & bset) / max(1, len(aset | bset))
    return exact, component, overlap


def _target_candidates(prop: str, source_index: int, seq: list[dict]) -> list[dict]:
    if prop in ("REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT"):
        return seq[:source_index]
    return seq[:source_index] + seq[source_index + 1 :]


def _target_score(prop: str, source: dict, target: dict) -> float:
    exact, component, overlap = _similarity(source, target)
    distance = abs(int(source["row"]["record_event_ordinal"]) - int(target["row"]["record_event_ordinal"]))
    near = 1.0 / (1.0 + distance)
    same_line = float(source["row"].get("line_id") == target["row"].get("line_id"))
    same_layout = float(source["row"].get("layout_role") == target["row"].get("layout_role"))
    if prop == "GENERIC_RELATION":
        score = 0.34 * exact + 0.22 * component + 0.18 * overlap + 0.18 * near + 0.08 * same_line
    elif prop == "COORDINATOR_RELATION":
        score = 0.18 * exact + 0.22 * component + 0.14 * overlap + 0.28 * near + 0.12 * same_line + 0.06 * same_layout
    elif prop == "ALTERNATIVE_RELATION":
        score = 0.08 * exact + 0.28 * component + 0.26 * overlap + 0.20 * near + 0.10 * same_line + 0.08 * same_layout
    elif prop == "REFERENCE_ANAPHORA":
        score = 0.46 * exact + 0.25 * component + 0.12 * overlap + 0.17 * near
    elif prop == "ENTITY_REUSE_ANTECEDENT":
        score = 0.61 * exact + 0.23 * component + 0.06 * overlap + 0.10 * near
    else:
        raise ValueError(prop)
    return round(min(0.999999, max(0.000001, score)), 8)


def _held_items(model: dict, held_rows: list[dict]) -> tuple[list[dict], dict[str, list[dict]]]:
    records: dict[str, list[dict]] = defaultdict(list)
    for row in held_rows:
        records[str(row["record_id"])].append(row)
    for seq in records.values():
        seq.sort(key=lambda r: (int(r.get("record_event_ordinal", 0)), int(r.get("event_index", 0)), str(r["event_id"])))
    items = []
    item_records: dict[str, list[dict]] = {}
    for record_id, seq in sorted(records.items()):
        prior = Counter()
        built = []
        for i, row in enumerate(seq):
            units = _surface_units(row)
            surface = _surface_key(units)
            info = model["types"].get(surface)
            component, comp_info, comp_start, comp_end = _best_component(model, units)
            prev_surface = _surface_key(_surface_units(seq[i - 1])) if i else ""
            next_surface = _surface_key(_surface_units(seq[i + 1])) if i + 1 < len(seq) else ""
            prev_component = _best_component(model, _surface_units(seq[i - 1]))[0] if i else ""
            next_component = _best_component(model, _surface_units(seq[i + 1]))[0] if i + 1 < len(seq) else ""
            item = {
                "model": model, "row": row, "units": units, "surface": surface,
                "type_info": info, "component": component, "component_info": comp_info,
                "component_start": comp_start, "component_end": comp_end,
                "prev_surface": prev_surface, "next_surface": next_surface,
                "prev_info": model["types"].get(prev_surface), "next_info": model["types"].get(next_surface),
                "prev_component": prev_component, "next_component": next_component,
                "prior_exact": prior[surface],
                "record_length_bin": _bin(float(len(seq)), model["record_length_cuts"]),
                "ordinal_bin": min(3, int(4 * i / max(1, len(seq)))),
            }
            prior[surface] += 1
            items.append(item)
            built.append(item)
        item_records[record_id] = built
    items.sort(key=lambda item: (int(item["row"].get("event_index", 0)), str(item["row"]["event_id"])))
    return items, item_records


def _architecture_signals(model: dict, held_metrics: dict[str, float]) -> tuple[float, ...]:
    means = model["architecture"]["means"]
    # Five independently measured, bounded observation-only signals matching
    # the preregistered families.  Three or more drive the multi decision.
    recurrence = held_metrics["repetition_rate"]
    context = held_metrics["boundary_stability"]
    relation = min(1.0, held_metrics["within_record_reuse"] * 3.0)
    scope_or_morph = held_metrics["component_proxy"]
    schema = min(1.0, held_metrics["schema_signal"] * 4.0)
    # Mild train anchoring stabilizes channel/seed sampling without labels.
    return tuple(round(min(1.0, max(0.0, 0.75 * value + 0.25 * anchor)), 8) for value, anchor in (
        (recurrence, means["repetition_rate"]),
        (context, means["boundary_stability"]),
        (relation, min(1.0, means["within_record_reuse"] * 3.0)),
        (scope_or_morph, means["component_proxy"]),
        (schema, min(1.0, means["schema_signal"] * 4.0)),
    ))


def decode(model: dict, held_rows: list[dict], representation: str) -> dict[str, list[dict]]:
    """Decode one held seed without modifying the canonical model."""
    if representation not in REPRESENTATIONS:
        raise ValueError(f"unsupported representation: {representation}")
    if not held_rows:
        raise ValueError("decode requires nonempty held rows")
    seeds = {int(row["corpus_seed"]) for row in held_rows}
    worlds = {str(row["world_id"]) for row in held_rows}
    surfaces = {str(row["surface_id"]) for row in held_rows}
    if len(seeds) != 1 or worlds != {model["world_id"]} or surfaces != {model["surface_id"]}:
        raise ValueError("decode requires one held seed matching fitted world/surface")
    outputs = {name: [] for name in TABLES}
    items, records = _held_items(model, held_rows)

    for item in items:
        row = item["row"]
        for prop in PARTITION_PROPERTIES:
            resolved, cluster, confidence = _partition_value(prop, item, representation)
            outputs["partition_claims"].append({
                **_common(row, representation, "PRIMARY", prop),
                "unit_type": "EVENT", "unit_id": str(row["event_id"]),
                "claim_status": "RESOLVED" if resolved else "ABSTAIN",
                "cluster_id": cluster if resolved else "", "confidence": confidence if resolved else 0.0,
            })
            if representation == "MULTI_RESOLUTION" and prop == "FUNCTION_OPERATOR_CLASS":
                multi_signals = _signals(model, item)
                multi_bin = int(_hid("", "function-multi", multi_signals, size=8), 16) % CLUSTER_BUDGET
                scalar = _event_scalar(model, item["units"], item["type_info"])
                scalar_bin = _bin(scalar, model["event_scalar"]["cuts"])
                # Coverage and maximum cluster capacity are exactly matched.
                for method, cluster_id, conf in (
                    ("MULTI_CONSTRAINT", f"fm_{multi_bin}", 0.58 + 0.08 * sum(x > 0 for x in multi_signals)),
                    ("SCALAR_BOTTLENECK", f"fs_{scalar_bin}", 0.58),
                ):
                    outputs["partition_claims"].append({
                        **_common(row, representation, method, prop),
                        "unit_type": "EVENT", "unit_id": str(row["event_id"]),
                        "claim_status": "RESOLVED", "cluster_id": cluster_id,
                        "confidence": round(min(0.98, conf), 8),
                    })

        comp_info = item["component_info"]
        productive = bool(comp_info and comp_info["status"] == "CURRENTLY_PRODUCTIVE")
        fossil = bool(comp_info and comp_info["status"] == "FOSSILIZED")
        sig = _signals(model, item)
        temporal = bool(sig[1] >= 1 and sig[2] >= 1 and (str(row.get("separator_after")) == "JOIN" or item["ordinal_bin"] in (0, 3)))
        reuse = bool(item["prior_exact"] > 0)
        binary_values = {
            "PRODUCTIVE_MORPHOLOGY": productive,
            "FOSSILIZED_MORPHOLOGY": fossil,
            "TEMPORAL_STATE_GATE": temporal,
            "ENTITY_REUSE_PRESENT": reuse,
        }
        for prop, value in binary_values.items():
            outputs["binary_claims"].append({
                **_common(row, representation, "PRIMARY", prop),
                "unit_type": "EVENT", "unit_id": str(row["event_id"]),
                "claim_status": "RESOLVED", "predicted_bool": bool(value),
                "confidence": _confidence(item["type_info"] is not None, 0.72 if value else 0.45),
            })

        # One explicit morphology row per event, including abstentions.
        if comp_info:
            scale = 2 if row["surface_id"] == "VOYNICH_SURFACE" else 1
            outputs["morphology_claims"].append({
                **_common(row, representation, "PRIMARY", "MORPHOLOGY_ANALYSIS"),
                "event_id": str(row["event_id"]), "component_id": str(comp_info["id"]),
                "start_offset": int(item["component_start"] * scale),
                "end_offset": int(item["component_end"] * scale),
                "morphology_status": str(comp_info["status"]), "claim_status": "RESOLVED",
                "rank": 1, "confidence": float(comp_info["confidence"]),
            })
        else:
            outputs["morphology_claims"].append({
                **_common(row, representation, "PRIMARY", "MORPHOLOGY_ANALYSIS"),
                "event_id": str(row["event_id"]), "component_id": "",
                "start_offset": 0, "end_offset": 0,
                "morphology_status": "NO_COMPONENT_CLAIM", "claim_status": "ABSTAIN",
                "rank": 1, "confidence": 0.0,
            })

    # Candidate policies are fixed and observation-only: generic/coordinator/
    # alternative use all other events in the same record; reference/reuse use
    # strictly earlier events in that record.  Only the best five are emitted.
    for record_id, seq in sorted(records.items()):
        for source_index, source in enumerate(seq):
            row = source["row"]
            for prop in TARGET_PROPERTIES:
                candidates = _target_candidates(prop, source_index, seq)
                candidate_id = (
                    "PRIOR_SEED_EVENTS"
                    if prop in ("REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT")
                    else "RECORD_EXCL_SELF"
                )
                scored = [(_target_score(prop, source, target), str(target["row"]["event_id"]), target) for target in candidates]
                scored.sort(key=lambda x: (-x[0], x[1]))
                chosen = scored[:RANK_CAP]
                status = "RESOLVED" if chosen else "ABSTAIN"
                outputs["target_queries"].append({
                    **_common(row, representation, "PRIMARY", prop),
                    "source_event_id": str(row["event_id"]), "candidate_set_id": candidate_id,
                    "claim_status": status, "predicted_target_count": len(chosen),
                    "confidence": round(chosen[0][0] if chosen else 0.0, 8),
                })
                for rank, (score, target_id, target) in enumerate(chosen, 1):
                    exact, component, _ = _similarity(source, target)
                    outputs["target_ranks"].append({
                        **_common(row, representation, "PRIMARY", prop),
                        "source_event_id": str(row["event_id"]), "candidate_set_id": candidate_id,
                        "target_rank": rank, "target_event_id": target_id,
                        "target_score": score,
                        "type_id": _hid("rt_", prop, int(exact), int(component), source["ordinal_bin"], target["ordinal_bin"]),
                    })

            # Scope is a bounded forward physical-line span.  Gate candidacy is
            # conjunctive; negative claims have empty endpoints by construction.
            sig = _signals(model, source)
            present = bool(sig[1] >= 1 and sig[2] >= 1 and source_index + 1 < len(seq))
            if present:
                start_i = source_index + 1
                end_i = start_i
                for j in range(start_i, min(len(seq), start_i + 4)):
                    if seq[j]["row"].get("line_id") != source["row"].get("line_id") and j > start_i:
                        break
                    end_i = j
                    if str(seq[j]["row"].get("separator_after", "")) in {"FIELD", "LINE", "PARAGRAPH", "PAGE"}:
                        break
                start_id = str(seq[start_i]["row"]["event_id"])
                end_id = str(seq[end_i]["row"]["event_id"])
            else:
                start_id = ""
                end_id = ""
            outputs["scope_claims"].append({
                **_common(row, representation, "PRIMARY", "SCOPE"),
                "source_event_id": str(row["event_id"]), "claim_status": "RESOLVED",
                "scope_present": bool(present), "predicted_start_event_id": start_id,
                "predicted_end_event_id": end_id,
                "scope_type_id": _hid("st_", "forward-line", source["ordinal_bin"]),
                "confidence": _confidence(source["type_info"] is not None, 0.7 if present else 0.4),
            })

        first = seq[0]["row"]
        surfaces = [item["surface"] for item in seq]
        repeated = sum(n for n in Counter(surfaces).values() if n > 1) / len(seq)
        layouts = tuple(sorted(Counter(str(item["row"].get("layout_role", "NA")) for item in seq).items()))
        separators = tuple(sorted(Counter(str(item["row"].get("separator_after", "NA")) for item in seq).items()))
        record_cluster = _hid("rs_", _bin(float(len(seq)), model["record_length_cuts"]), layouts, separators, round(repeated, 1))
        outputs["record_partition_claims"].append({
            **_common(first, representation, "PRIMARY", "RECORD_SCHEMA"),
            "record_id": record_id, "claim_status": "RESOLVED",
            "record_schema_cluster_id": record_cluster,
            "confidence": round(min(0.95, 0.58 + 0.18 * repeated + 0.03 * min(4, len(layouts))), 8),
        })

    first_row = items[0]["row"]
    held_metrics = _architecture_metrics(held_rows)
    arch_signals = _architecture_signals(model, held_metrics)
    primary_cluster = _hid("wa_", tuple(round(x, 1) for x in arch_signals), _bin(held_metrics["mean_group_length"], [2, 3, 5, 7]))
    outputs["architecture_partition_claims"].append({
        **_common(first_row, representation, "PRIMARY", "WORLD_ARCHITECTURE"),
        "claim_status": "RESOLVED", "architecture_cluster_id": primary_cluster,
        "confidence": round(0.5 + 0.4 * fmean(arch_signals), 8),
    })
    scalar_name = model["architecture"]["scalar_name"]
    scalar_value = held_metrics[scalar_name]
    scalar_bin = _bin(scalar_value, model["architecture"]["scalar_cuts"])
    multi_bin = int(_hid("", "architecture-multi", tuple(round(x, 2) for x in arch_signals), size=8), 16) % ARCHITECTURE_CLUSTER_BUDGET
    if representation == "MULTI_RESOLUTION":
        for method, cluster, confidence in (
            ("MULTI_CONSTRAINT", f"am_{multi_bin}", 0.55 + 0.07 * sum(x >= 0.5 for x in arch_signals)),
            ("SCALAR_BOTTLENECK", f"as_{scalar_bin}", 0.58),
        ):
            outputs["architecture_partition_claims"].append({
                **_common(first_row, representation, method, "WORLD_ARCHITECTURE"),
                "claim_status": "RESOLVED", "architecture_cluster_id": cluster,
                "confidence": round(min(0.98, confidence), 8),
            })

    multi_positive = sum(value >= 0.5 for value in arch_signals) >= 3 and any(value >= 0.5 for value in arch_signals[2:])
    primary_flags = {
        "LANGUAGE_LIKE": arch_signals[1] >= 0.55 and held_metrics["unigram_entropy"] >= 2.0,
        "NOTATION_LIKE": arch_signals[4] >= 0.45 and held_metrics["mean_group_length"] <= 3.5,
        "CODEBOOK_LIKE": arch_signals[0] >= 0.75 and held_metrics["type_token_ratio"] <= 0.18,
        "ORGANIC_EVOLUTION_LIKE": arch_signals[3] >= 0.35 and held_metrics["type_token_ratio"] >= 0.02,
        "CLEAN_ENGINEERED_LIKE": multi_positive and arch_signals[1] >= 0.65,
        "SEMANTICS_LIGHT_LIKE": arch_signals[2] >= 0.65 and arch_signals[3] < 0.45,
    }
    scalar_rank = scalar_bin / max(1, ARCHITECTURE_CLUSTER_BUDGET - 1)
    scalar_flags = {
        "LANGUAGE_LIKE": scalar_rank >= 0.50,
        "NOTATION_LIKE": scalar_rank < 0.34,
        "CODEBOOK_LIKE": scalar_rank >= 0.67,
        "ORGANIC_EVOLUTION_LIKE": 0.34 <= scalar_rank < 0.84,
        "CLEAN_ENGINEERED_LIKE": scalar_rank >= 0.84,
        "SEMANTICS_LIGHT_LIKE": scalar_rank < 0.17,
    }
    multi_flags = dict(primary_flags)
    multi_flags["CLEAN_ENGINEERED_LIKE"] = bool(multi_positive)
    for prop in ARCHITECTURE_PROPERTIES:
        outputs["architecture_binary_claims"].append({
            **_common(first_row, representation, "PRIMARY", prop),
            "claim_status": "RESOLVED", "predicted_bool": bool(primary_flags[prop]),
            "confidence": round(0.55 + 0.32 * abs(fmean(arch_signals) - 0.5) * 2, 8),
        })
        if representation == "MULTI_RESOLUTION":
            for method, flags, confidence in (
                ("MULTI_CONSTRAINT", multi_flags, 0.62 + 0.04 * sum(x >= 0.5 for x in arch_signals)),
                ("SCALAR_BOTTLENECK", scalar_flags, 0.58 + 0.22 * abs(scalar_rank - 0.5) * 2),
            ):
                outputs["architecture_binary_claims"].append({
                    **_common(first_row, representation, method, prop),
                    "claim_status": "RESOLVED", "predicted_bool": bool(flags[prop]),
                    "confidence": round(min(0.98, confidence), 8),
                })
    return outputs


def classify_world(model: dict) -> list[dict]:
    """Return train-only anonymous architecture summaries.

    The runner-facing held architecture claims are emitted by ``decode``.  This
    function deliberately exposes no readable class names or hidden labels.
    """
    means = model["architecture"]["means"]
    signals = _architecture_signals(model, means)
    scalar_name = model["architecture"]["scalar_name"]
    scalar_value = means[scalar_name]
    scalar_bin = _bin(scalar_value, model["architecture"]["scalar_cuts"])
    multi_bin = int(_hid("", "architecture-multi", tuple(round(x, 2) for x in signals), size=8), 16) % ARCHITECTURE_CLUSTER_BUDGET
    return [
        {
            "method_variant": "PRIMARY",
            "claim_status": "RESOLVED",
            "architecture_cluster_id": _hid("wa_", tuple(round(x, 1) for x in signals)),
            "confidence": round(0.5 + 0.4 * fmean(signals), 8),
        },
        {
            "method_variant": "MULTI_CONSTRAINT",
            "claim_status": "RESOLVED",
            "architecture_cluster_id": f"am_{multi_bin}",
            "confidence": round(min(0.98, 0.55 + 0.07 * sum(x >= 0.5 for x in signals)), 8),
        },
        {
            "method_variant": "SCALAR_BOTTLENECK",
            "claim_status": "RESOLVED",
            "architecture_cluster_id": f"as_{scalar_bin}",
            "confidence": 0.58,
        },
    ]
