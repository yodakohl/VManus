#!/usr/bin/env python3
"""Blind GDT396 train-only register-contrastive latent-role decoder.

The implementation deliberately uses no ontology.  It discovers surface types,
recurrent proper substrings, and anonymous roles defined by intersections of
register, layout, position, boundary, and local recurrence features.  Held-seed
aggregation is transductive only within the supplied packet and never mutates
the fitted model.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from typing import Iterable


API_VERSION = 2
DECODER_META = {
    "api_version": API_VERSION,
    "decoder_id": "d396s04_contrastive_roles",
    "designer_model": "GPT-5.6-Sol",
    "method_family": "register_contrastive_multiresolution_latent_roles",
    "oracle_blind": True,
    "supported_representations": [
        "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
        "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY", "MULTI_RESOLUTION",
    ],
    "supported_claim_kinds": [
        "partition_claims", "binary_claims", "target_queries", "target_ranks",
        "scope_claims", "morphology_claims", "record_partition_claims",
        "architecture_partition_claims", "architecture_binary_claims",
    ],
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

TABLES = (
    "partition_claims", "binary_claims", "target_queries", "target_ranks",
    "scope_claims", "morphology_claims", "record_partition_claims",
    "architecture_partition_claims", "architecture_binary_claims",
)
ARCH_FLAGS = (
    "LANGUAGE_LIKE", "NOTATION_LIKE", "CODEBOOK_LIKE",
    "ORGANIC_EVOLUTION_LIKE", "CLEAN_ENGINEERED_LIKE",
    "SEMANTICS_LIGHT_LIKE",
)


def _hash(prefix: str, value: object, size: int = 16) -> str:
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:size]


def _surface(row: dict) -> tuple:
    value = row["visible_surface"]
    return tuple(value) if not isinstance(value, tuple) else value


def _surface_key(value: Iterable) -> str:
    return json.dumps(list(value), ensure_ascii=True, separators=(",", ":"))


def _surface_from_key(key: str) -> tuple:
    return tuple(json.loads(key))


def _analysis_tokens(row: dict) -> tuple:
    """Return channel-normalized analysis tokens, not output offsets."""
    raw = _surface(row)
    if row.get("surface_id") == "VOYNICH_SURFACE" and len(raw) % 2 == 0:
        return tuple(_surface_key(raw[i:i + 2]) for i in range(0, len(raw), 2))
    return raw


def _analysis_key(row: dict) -> str:
    return _surface_key(_analysis_tokens(row))


def _bucket(value: float, cuts: tuple[float, ...]) -> int:
    return sum(value >= cut for cut in cuts)


def _entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total <= 1 or len(counts) <= 1:
        return 0.0
    h = -sum((n / total) * math.log(n / total) for n in counts.values() if n)
    return h / math.log(len(counts))


def _concentration(counts: Counter) -> float:
    total = sum(counts.values())
    return max(counts.values(), default=0) / total if total else 0.0


def _dominant(counts: Counter) -> str:
    return min((-n, str(k)) for k, n in counts.items())[1] if counts else "_"


def _profile_signature(profile: dict, total_records: int) -> list:
    n = profile["n"]
    return [
        _bucket(math.log2(n + 1), (1.5, 3.0, 5.0, 7.0)),
        _bucket(profile["length"], (1.5, 2.5, 4.5, 7.5)),
        _bucket(profile["record_n"] / max(1, total_records), (.01, .05, .20, .50)),
        _bucket(_concentration(profile["register"]), (.40, .65, .85)),
        _bucket(_concentration(profile["layout"]), (.40, .65, .85)),
        _bucket(_entropy(profile["prev"]), (.20, .50, .80)),
        _bucket(_entropy(profile["next"]), (.20, .50, .80)),
        _dominant(profile["register"]), _dominant(profile["layout"]),
        _dominant(profile["record_pos"]), _dominant(profile["line_pos"]),
        _dominant(profile["before"]), _dominant(profile["after"]),
    ]


def _role_id(profile: dict, total_records: int) -> str:
    return _hash("r", _profile_signature(profile, total_records), 14)


def _blank_profile(length: int) -> dict:
    return {
        "n": 0, "length": length, "record_n": 0,
        "register": Counter(), "layout": Counter(), "record_pos": Counter(),
        "line_pos": Counter(), "before": Counter(), "after": Counter(),
        "prev": Counter(), "next": Counter(),
    }


def _profiles(rows: list[dict]) -> tuple[dict[str, dict], dict[tuple, list[dict]]]:
    records: dict[tuple, list[dict]] = defaultdict(list)
    type_records: dict[str, set] = defaultdict(set)
    profiles: dict[str, dict] = {}
    for row in rows:
        rec = (int(row["corpus_seed"]), str(row["record_id"]))
        records[rec].append(row)
        key = _analysis_key(row)
        if key not in profiles:
            profiles[key] = _blank_profile(len(_analysis_tokens(row)))
        p = profiles[key]
        p["n"] += 1
        p["register"][str(row.get("register_id", "_"))] += 1
        p["layout"][str(row.get("layout_role", "_"))] += 1
        p["record_pos"][str(row.get("record_position_bin", "_"))] += 1
        p["line_pos"][str(row.get("line_position_bin", "_"))] += 1
        p["before"][str(row.get("separator_before", "_"))] += 1
        p["after"][str(row.get("separator_after", "_"))] += 1
        type_records[key].add(rec)
    for rec_rows in records.values():
        rec_rows.sort(key=lambda r: int(r["record_event_ordinal"]))
        keys = [_analysis_key(r) for r in rec_rows]
        for i, key in enumerate(keys):
            profiles[key]["prev"][keys[i - 1] if i else "^BOUNDARY"] += 1
            profiles[key]["next"][keys[i + 1] if i + 1 < len(keys) else "$BOUNDARY"] += 1
    for key, p in profiles.items():
        p["record_n"] = len(type_records[key])
        # Kept only in the live fit/held aggregation.  It is intentionally not
        # serialized by _json_profile because no event provenance is needed at
        # decode time.
        p["record_ids"] = type_records[key]
    return profiles, records


def _json_profile(profile: dict) -> dict:
    return {
        "n": profile["n"], "length": profile["length"],
        "record_n": profile["record_n"],
        **{name: dict(sorted(profile[name].items())) for name in (
            "register", "layout", "record_pos", "line_pos", "before", "after",
            "prev", "next",
        )},
    }


def _live_profile(profile: dict) -> dict:
    return {
        "n": int(profile["n"]), "length": int(profile["length"]),
        "record_n": int(profile["record_n"]),
        **{name: Counter(profile[name]) for name in (
            "register", "layout", "record_pos", "line_pos", "before", "after",
            "prev", "next",
        )},
    }


def _component_candidates(profiles: dict[str, dict]) -> list[dict]:
    supports: dict[tuple, set[str]] = defaultdict(set)
    positions: dict[tuple, Counter] = defaultdict(Counter)
    residuals: dict[tuple, set[str]] = defaultdict(set)
    roles: dict[tuple, set[str]] = defaultdict(set)
    component_records: dict[tuple, set] = defaultdict(set)
    all_records = set().union(*(p["record_ids"] for p in profiles.values())) if profiles else set()
    total_records = max(1, len(all_records))
    for key, profile in profiles.items():
        seq = _surface_from_key(key)
        role = _role_id(profile, total_records)
        limit = min(3, len(seq) - 1)
        seen = set()
        for width in range(1, limit + 1):
            candidates = ((tuple(seq[:width]), "P", tuple(seq[width:])),
                          (tuple(seq[-width:]), "S", tuple(seq[:-width])))
            if len(seq) >= width + 2:
                start = (len(seq) - width) // 2
                candidates += ((tuple(seq[start:start + width]), "I",
                                tuple(seq[:start] + seq[start + width:])),)
            for comp, pos, residual in candidates:
                marker = (comp, pos)
                if marker in seen:
                    continue
                seen.add(marker)
                supports[comp].add(key)
                positions[comp][pos] += 1
                residuals[comp].add(_surface_key(residual))
                roles[comp].add(role)
                component_records[comp].update(profile["record_ids"])
    ranked = []
    vocabulary_n = max(1, len(profiles))
    for comp, type_set in supports.items():
        type_n = len(type_set)
        residual_n = len(residuals[comp])
        type_fraction = type_n / vocabulary_n
        if (type_n < 4 or residual_n < 4 or len(component_records[comp]) < 2 or
                type_fraction > (.35 if len(comp) == 1 else .60)):
            continue
        pos_conc = _concentration(positions[comp])
        if pos_conc < .60:
            continue
        role_n = len(roles[comp])
        diversity = min(1.0, math.log2(residual_n + 1) / 5.0)
        breadth = min(1.0, math.log2(type_n + 1) / 7.0)
        productivity = .45 * diversity + .30 * breadth + .15 * pos_conc + .10 * min(1, role_n / 3)
        if productivity >= .62 and role_n >= 2:
            status = "CURRENTLY_PRODUCTIVE"
        elif pos_conc >= .75 and role_n <= max(4, int(math.sqrt(type_n))):
            status = "FOSSILIZED"
        else:
            continue
        score = productivity if status == "CURRENTLY_PRODUCTIVE" else .40 * breadth + .35 * pos_conc + .25 * (1 - min(1, role_n / 4))
        ranked.append({
            "component_id": _hash("m", [list(comp), status], 14),
            "tokens": list(comp), "status": status,
            "score": round(min(.99, .45 + .5 * score), 6),
            "support_types": type_n,
        })
    ranked.sort(key=lambda c: (-c["score"], -c["support_types"], c["component_id"]))
    # Cap the registry and keep the two status inventories explicitly disjoint.
    selected, used = [], set()
    by_status = Counter()
    for item in ranked:
        marker = tuple(item["tokens"])
        if marker in used or by_status[item["status"]] >= 48:
            continue
        used.add(marker); by_status[item["status"]] += 1; selected.append(item)
    return selected


def _architecture(signals: dict[str, float]) -> list[dict]:
    eq = signals["partition"]
    stable = signals["stability"]
    relation = signals["relation"]
    morph = signals["morphology"]
    schema = signals["schema"]
    primary = .24 * eq + .20 * stable + .21 * relation + .18 * morph + .17 * schema
    votes = [eq >= .55, stable >= .50, relation >= .45, morph >= .40, schema >= .45]
    multi_bool = sum(votes) >= 3 and any(votes[2:])
    multi = (.18 * eq + .18 * stable + .24 * relation + .20 * morph + .20 * schema)
    scalar = signals["repetition"]

    def flags(score: float, variant: str) -> dict[str, list]:
        if variant == "SCALAR_BOTTLENECK":
            # Matched one-dimensional comparator: every flag is a function of
            # the single frozen repetition statistic and nothing else.
            return {
                "LANGUAGE_LIKE": [0.30 <= score < 0.85, .66],
                "NOTATION_LIKE": [score >= 0.80, .66],
                "CODEBOOK_LIKE": [score >= 0.90, .66],
                "ORGANIC_EVOLUTION_LIKE": [0.40 <= score < 0.85, .66],
                "CLEAN_ENGINEERED_LIKE": [score >= 0.94, .66],
                "SEMANTICS_LIGHT_LIKE": [score < 0.30, .66],
            }
        structured = multi_bool if variant == "MULTI_CONSTRAINT" else score >= .56
        low_semantic_proxy = eq >= .45 and relation < .38 and morph < .32 and schema < .42
        return {
            "LANGUAGE_LIKE": [structured and stable >= .45, .50 + .45 * abs(stable - .45)],
            "NOTATION_LIKE": [structured and schema >= .55, .50 + .45 * abs(schema - .55)],
            "CODEBOOK_LIKE": [eq >= .72 and morph < .52, .50 + .45 * abs(eq - morph)],
            "ORGANIC_EVOLUTION_LIKE": [morph >= .52 and stable >= .40, .50 + .4 * min(morph, stable)],
            "CLEAN_ENGINEERED_LIKE": [schema >= .68 and relation >= .48, .50 + .35 * min(schema, relation)],
            "SEMANTICS_LIGHT_LIKE": [low_semantic_proxy, .50 + .35 * max(0.0, eq - max(relation, morph, schema))],
        }

    return [
        {"method_variant": "PRIMARY", "score": round(primary, 6), "positive": primary >= .56,
         "cluster": _hash("a", [round(x, 1) for x in signals.values()], 12), "flags": flags(primary, "PRIMARY")},
        {"method_variant": "MULTI_CONSTRAINT", "score": round(multi, 6), "positive": multi_bool,
         "cluster": _hash("a", [int(x) for x in votes], 12), "flags": flags(multi, "MULTI_CONSTRAINT")},
        {"method_variant": "SCALAR_BOTTLENECK", "score": round(scalar, 6), "positive": scalar >= .72,
         "cluster": _hash("a", ["repetition_rate", round(scalar, 1)], 12), "flags": flags(scalar, "SCALAR_BOTTLENECK")},
    ]


def fit(train_rows: list[dict]) -> dict:
    if not train_rows:
        raise ValueError("fit requires nonempty training rows")
    worlds = {str(r["world_id"]) for r in train_rows}
    surfaces = {str(r["surface_id"]) for r in train_rows}
    if len(worlds) != 1 or len(surfaces) != 1:
        raise ValueError("fit requires one world and one surface channel")
    profiles, records = _profiles(train_rows)
    total_records = len(records)
    roles = {key: _role_id(p, total_records) for key, p in profiles.items()}
    role_counts = Counter(roles[_analysis_key(r)] for r in train_rows)
    transitions = Counter()
    surface_links: dict[str, Counter] = defaultdict(Counter)
    schema_counts = Counter()
    for rec_rows in records.values():
        role_seq = [roles[_analysis_key(r)] for r in rec_rows]
        compressed = [role_seq[0]] if role_seq else []
        for role in role_seq[1:]:
            if role != compressed[-1]:
                compressed.append(role)
        schema = _hash("s", [min(7, len(rec_rows) // 4), compressed[:8]], 14)
        schema_counts[schema] += 1
        keys = [_analysis_key(r) for r in rec_rows]
        for i, (source_key, source_role) in enumerate(zip(keys, role_seq)):
            lo, hi = max(0, i - 6), min(len(keys), i + 7)
            for j in range(lo, hi):
                if i == j:
                    continue
                delta = j - i
                direction = -1 if delta < 0 else 1
                distance = min(3, abs(delta))
                transitions[(source_role, role_seq[j], direction, distance)] += 1
                surface_links[source_key][keys[j]] += max(1, 7 - abs(delta))
    components = _component_candidates(profiles)
    component_tokens = [tuple(c["tokens"]) for c in components if c["status"] == "CURRENTLY_PRODUCTIVE"]
    covered = 0
    for key in profiles:
        seq = _surface_from_key(key)
        if any(len(c) < len(seq) and _find_subsequence(seq, c) >= 0 for c in component_tokens):
            covered += profiles[key]["n"]
    n = len(train_rows)
    type_n = len(profiles)
    repeat = 1.0 - type_n / max(1, n)
    stability = sum(p["n"] * (.5 * _concentration(p["register"]) + .5 * _concentration(p["layout"])) for p in profiles.values()) / max(1, n)
    # Context predictability above the strongest marginal role is a blind
    # relation-lift proxy; raw transition volume would be a vacuous signal.
    transition_groups: dict[tuple, Counter] = defaultdict(Counter)
    for (source_role, target_role, direction, distance), count in transitions.items():
        transition_groups[(source_role, direction, distance)][target_role] += count
    marginal = max(role_counts.values(), default=0) / max(1, n)
    lift_weight = lift_total = 0.0
    for counter in transition_groups.values():
        group_n = sum(counter.values())
        concentration = max(counter.values(), default=0) / max(1, group_n)
        lift = max(0.0, concentration - marginal) / max(1e-9, 1.0 - marginal)
        lift_weight += group_n * lift
        lift_total += group_n
    relation = lift_weight / max(1.0, lift_total)
    morphology = covered / max(1, n)
    schema = sum(v for v in schema_counts.values() if v >= 2) / max(1, total_records)
    signals = {
        "partition": round(repeat, 6), "stability": round(stability, 6),
        "relation": round(relation, 6), "morphology": round(morphology, 6),
        "schema": round(schema, 6), "repetition": round(repeat, 6),
    }
    top_links = {}
    for source, counter in surface_links.items():
        top_links[source] = [[target, count] for target, count in sorted(counter.items(), key=lambda x: (-x[1], x[0]))[:12]]
    return {
        "api_version": API_VERSION,
        "decoder_id": DECODER_META["decoder_id"],
        "world_id": next(iter(worlds)), "surface_id": next(iter(surfaces)),
        "train_event_count": n, "train_record_count": total_records,
        "profiles": {k: _json_profile(v) for k, v in sorted(profiles.items())},
        "roles": dict(sorted(roles.items())),
        "role_counts": dict(sorted(role_counts.items())),
        "transitions": [[*key, count] for key, count in sorted(transitions.items())],
        "surface_links": dict(sorted(top_links.items())),
        "components": components,
        "signals": signals,
        "architecture": _architecture(signals),
        "scalar_feature": "repetition_rate",
    }


def classify_world(model: dict) -> list[dict]:
    """Return immutable, seed-agnostic architecture descriptors."""
    return json.loads(json.dumps(model["architecture"], sort_keys=True))


def _find_subsequence(seq: tuple, part: tuple) -> int:
    if not part or len(part) > len(seq):
        return -1
    for i in range(len(seq) - len(part) + 1):
        if seq[i:i + len(part)] == part:
            return i
    return -1


def _held_roles(rows: list[dict], model: dict) -> tuple[dict[str, str], dict[tuple, list[dict]], dict[str, dict]]:
    profiles, records = _profiles(rows)
    total_records = len(records)
    roles = {}
    for key, profile in profiles.items():
        roles[key] = model["roles"].get(key, _role_id(profile, total_records))
    return roles, records, profiles


def _common(row: dict, representation: str, variant: str, prop: str) -> dict:
    return {
        "schema_version": API_VERSION,
        "phase": str(row["phase"]), "run_id": str(row["run_id"]),
        "world_id": str(row["world_id"]), "corpus_seed": int(row["corpus_seed"]),
        "surface_id": str(row["surface_id"]), "representation_id": representation,
        "decoder_id": DECODER_META["decoder_id"], "method_variant": variant,
        "property_id": prop,
    }


def _confidence(count: int, scale: float = 8.0) -> float:
    return round(min(.99, .50 + .49 * (1 - math.exp(-max(0, count) / scale))), 6)


def _matches(row: dict, components: list[dict]) -> list[tuple[dict, int]]:
    seq = _analysis_tokens(row)
    found = []
    for comp in components:
        part = tuple(comp["tokens"])
        start = _find_subsequence(seq, part)
        if start >= 0 and len(part) < len(seq):
            found.append((comp, start))
    found.sort(key=lambda x: (-x[0]["score"], -len(x[0]["tokens"]), x[0]["component_id"]))
    return found[:3]


def _target_score(source: dict, target: dict, prop: str, source_role: str,
                  target_role: str, model: dict, exact_link: dict[str, int]) -> float:
    si = int(source["record_event_ordinal"])
    ti = int(target["record_event_ordinal"])
    delta = ti - si
    distance = abs(int(source["global_event_rank"]) - int(target["global_event_rank"]))
    same = _analysis_key(source) == _analysis_key(target)
    role_same = source_role == target_role
    link = exact_link.get(_analysis_key(target), 0)
    proximity = 1.0 / (1.0 + distance)
    if prop == "GENERIC_RELATION":
        raw = .28 * proximity + .25 * min(1, link / 12) + .22 * role_same + .25 * same
    elif prop == "COORDINATOR_RELATION":
        raw = .38 * (abs(delta) == 1) + .28 * role_same + .20 * min(1, link / 10) + .14 * same
    elif prop == "ALTERNATIVE_RELATION":
        raw = .34 * role_same + .30 * same + .22 * min(1, link / 10) + .14 * proximity
    elif prop == "REFERENCE_ANAPHORA":
        raw = .38 * same + .28 * role_same + .22 * min(1, link / 10) + .12 * proximity
    else:
        raw = .60 * same + .20 * role_same + .20 * proximity
    return round(min(.99, .05 + .94 * raw), 6)


def decode(model: dict, held_rows: list[dict], representation: str) -> dict[str, list[dict]]:
    if representation not in DECODER_META["supported_representations"]:
        raise ValueError("unsupported representation")
    out = {name: [] for name in TABLES}
    if not held_rows:
        return out
    if {str(r["world_id"]) for r in held_rows} != {model["world_id"]}:
        raise ValueError("held world differs from fitted world")
    if {str(r["surface_id"]) for r in held_rows} != {model["surface_id"]}:
        raise ValueError("held surface differs from fitted surface")
    if len({int(r["corpus_seed"]) for r in held_rows}) != 1:
        raise ValueError("decode requires exactly one held seed")
    roles, records, held_profiles = _held_roles(held_rows, model)
    train_profiles = {k: _live_profile(v) for k, v in model["profiles"].items()}
    role_freq = Counter(roles[_analysis_key(r)] for r in held_rows)
    components = model["components"]
    # Index one representative row per visible type once.  The original
    # independent implementation rescanned every held event for every type;
    # this is exactly equivalent but quadratic on singleton-heavy channels.
    representative = {}
    for row in held_rows:
        representative.setdefault(_analysis_key(row), row)
    match_cache = {key: _matches(representative[key], components) for key in held_profiles}
    previous_by_key: dict[str, list[dict]] = defaultdict(list)
    previous_by_role: dict[str, list[dict]] = defaultdict(list)

    # Event partitions and typed binary/morphology outputs.
    component_reps = {"HOST_LIKE", "INFERRED_COMPONENTS", "MULTI_RESOLUTION"}
    role_reps = {"COMPOSITE_STATE", "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY", "MULTI_RESOLUTION"}
    for row in sorted(held_rows, key=lambda r: int(r["global_event_rank"])):
        key = _analysis_key(row); role = roles[key]
        count = int(model["profiles"].get(key, {}).get("n", held_profiles[key]["n"]))
        c = _confidence(count)
        if representation == "FULL_GROUP":
            base = _common(row, representation, "PRIMARY", "LEXICAL_IDENTITY")
            out["partition_claims"].append({**base, "unit_type": "EVENT", "unit_id": str(row["event_id"]),
                "claim_status": "RESOLVED", "cluster_id": _hash("x", key, 16), "confidence": c})
        role_properties = []
        if representation == "MULTI_RESOLUTION": role_properties.append(("FUNCTION_OPERATOR_CLASS", role))
        if representation == "HOST_LIKE": role_properties.append(("REGISTER_REALIZATION", [role, str(row.get("register_id", "_"))]))
        if representation == "COMPOSITE_STATE": role_properties.append(("CONSTRUCTION_CLASS", [role, str(row.get("record_position_bin", "_")), str(row.get("layout_role", "_"))]))
        if representation in role_reps:
            for prop, signature in role_properties:
                common = _common(row, representation, "PRIMARY", prop)
                out["partition_claims"].append({**common, "unit_type": "EVENT", "unit_id": str(row["event_id"]),
                    "claim_status": "RESOLVED", "cluster_id": _hash("c", signature, 14), "confidence": c})
        matches = match_cache[key]
        for prop, wanted in (("CURRENT_PRODUCTIVE_COMPONENT", "CURRENTLY_PRODUCTIVE"),
                             ("FOSSIL_COMPONENT", "FOSSILIZED")):
            if representation == "INFERRED_COMPONENTS":
                found = next((m for m in matches if m[0]["status"] == wanted), None)
                common = _common(row, representation, "PRIMARY", prop)
                out["partition_claims"].append({**common, "unit_type": "EVENT", "unit_id": str(row["event_id"]),
                    "claim_status": "RESOLVED" if found else "ABSTAIN",
                    "cluster_id": found[0]["component_id"] if found else _hash("u", prop, 12),
                    "confidence": found[0]["score"] if found else .5})
        productive = next((m for m in matches if m[0]["status"] == "CURRENTLY_PRODUCTIVE"), None)
        fossil = next((m for m in matches if m[0]["status"] == "FOSSILIZED"), None)
        reuse = bool(previous_by_key[key])
        gate = role_freq[role] >= 3 and (
            str(row.get("separator_before", "")) != str(row.get("separator_after", "")) or
            str(row.get("record_position_bin", "")).lower() in {"initial", "final", "start", "end"})
        binary_properties = []
        if representation == "INFERRED_COMPONENTS":
            binary_properties.extend((("PRODUCTIVE_MORPHOLOGY", bool(productive), productive[0]["score"] if productive else .62), ("FOSSILIZED_MORPHOLOGY", bool(fossil), fossil[0]["score"] if fossil else .62)))
        if representation == "COMPOSITE_STATE":
            binary_properties.append(("TEMPORAL_STATE_GATE", bool(gate), min(.95, .55 + role_freq[role] / max(20, len(held_rows)))))
        if representation == "RECORD_TOPOLOGY":
            binary_properties.append(("ENTITY_REUSE_PRESENT", reuse, .90 if reuse else .66))
        for prop, value, conf in binary_properties:
            common = _common(row, representation, "PRIMARY", prop)
            out["binary_claims"].append({**common, "unit_type": "EVENT", "unit_id": str(row["event_id"]),
                "claim_status": "RESOLVED", "predicted_bool": value, "confidence": round(conf, 6)})
        if representation == "INFERRED_COMPONENTS" and matches:
            raw_scale = 2 if row["surface_id"] == "VOYNICH_SURFACE" else 1
            for rank, (comp, start) in enumerate(matches, 1):
                common = _common(row, representation, "PRIMARY", "MORPHOLOGY_ANALYSIS")
                out["morphology_claims"].append({**common, "event_id": str(row["event_id"]),
                    "component_id": comp["component_id"], "start_offset": start * raw_scale,
                    "end_offset": (start + len(comp["tokens"])) * raw_scale,
                    "morphology_status": comp["status"], "claim_status": "RESOLVED",
                    "rank": rank, "confidence": comp["score"]})
        elif representation == "INFERRED_COMPONENTS":
            common = _common(row, representation, "PRIMARY", "MORPHOLOGY_ANALYSIS")
            out["morphology_claims"].append({**common, "event_id": str(row["event_id"]),
                "component_id": _hash("u", "NO_COMPONENT", 12), "start_offset": 0,
                "end_offset": 0, "morphology_status": "NO_COMPONENT_CLAIM",
                "claim_status": "ABSTAIN", "rank": 1, "confidence": .5})
        previous_by_key[key].append(row); previous_by_role[role].append(row)

    # Record schemas, ranked relations/references, and bounded scopes.
    # Precompute bounded top-k evidence pools in true held-seed event order.
    # This preserves the PRIOR_SEED_EVENTS universe even though records below
    # are traversed by record key for the within-record candidate universes.
    prior_pools: dict[str, list[dict]] = {}
    all_prior: list[dict] = []
    prior_key: dict[str, list[dict]] = defaultdict(list)
    prior_role: dict[str, list[dict]] = defaultdict(list)
    for row in sorted(held_rows, key=lambda r: int(r["global_event_rank"])):
        key = _analysis_key(row); role = roles[key]
        pool_map = {}
        for target in (all_prior[-20:] + prior_key[key][-8:] + prior_role[role][-8:]):
            pool_map[str(target["event_id"])] = target
        prior_pools[str(row["event_id"])] = list(pool_map.values())
        all_prior.append(row); prior_key[key].append(row); prior_role[role].append(row)
    for rec_key in sorted(records) if representation in {"RECORD_TOPOLOGY", "CONSTRUCTION_SPAN"} else ():
        rec_rows = records[rec_key]
        role_seq = [roles[_analysis_key(r)] for r in rec_rows]
        compressed = [role_seq[0]] if role_seq else []
        for role in role_seq[1:]:
            if role != compressed[-1]: compressed.append(role)
        schema = _hash("s", [min(7, len(rec_rows) // 4), compressed[:8]], 14)
        first = rec_rows[0]
        if representation == "RECORD_TOPOLOGY":
            common = _common(first, representation, "PRIMARY", "RECORD_SCHEMA")
            out["record_partition_claims"].append({**common, "record_id": str(first["record_id"]),
                "claim_status": "RESOLVED", "record_schema_cluster_id": schema,
                "confidence": _confidence(len(rec_rows), 12)})
        for i, source in enumerate(rec_rows):
            source_key = _analysis_key(source); source_role = roles[source_key]
            exact_link = dict(model["surface_links"].get(source_key, []))
            within = [target for j, target in enumerate(rec_rows) if j != i]
            for prop in (("GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION") if representation == "RECORD_TOPOLOGY" else ()):
                common = _common(source, representation, "PRIMARY", prop)
                if not within:
                    out["target_queries"].append({**common, "source_event_id": str(source["event_id"]),
                        "candidate_set_id": "RECORD_EXCL_SELF", "claim_status": "ABSTAIN",
                        "predicted_target_count": 0, "confidence": .5})
                    continue
                scored = [(_target_score(source, target, prop, source_role, roles[_analysis_key(target)], model, exact_link), target) for target in within]
                scored.sort(key=lambda x: (-x[0], int(x[1]["global_event_rank"]), str(x[1]["event_id"])))
                best = scored[:5]
                out["target_queries"].append({**common, "source_event_id": str(source["event_id"]),
                    "candidate_set_id": "RECORD_EXCL_SELF", "claim_status": "RESOLVED",
                    "predicted_target_count": len(best), "confidence": best[0][0]})
                for rank, (score, target) in enumerate(best, 1):
                    out["target_ranks"].append({**common, "source_event_id": str(source["event_id"]),
                        "candidate_set_id": "RECORD_EXCL_SELF", "target_rank": rank,
                        "target_event_id": str(target["event_id"]), "target_score": score,
                        "type_id": _hash("t", [prop, source_role, roles[_analysis_key(target)]], 12)})
            # The literal universe is all earlier events in this held seed.  A
            # compact evidence-driven pool is ranked, which is permitted for top-k output.
            pool = prior_pools[str(source["event_id"])]
            for prop in (("REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT") if representation == "RECORD_TOPOLOGY" else ()):
                common = _common(source, representation, "PRIMARY", prop)
                if not pool:
                    out["target_queries"].append({**common, "source_event_id": str(source["event_id"]),
                        "candidate_set_id": "PRIOR_SEED_EVENTS", "claim_status": "ABSTAIN",
                        "predicted_target_count": 0, "confidence": .5})
                    continue
                scored = [(_target_score(source, target, prop, source_role, roles[_analysis_key(target)], model, exact_link), target) for target in pool]
                scored.sort(key=lambda x: (-x[0], -int(x[1]["global_event_rank"]), str(x[1]["event_id"])))
                best = scored[:5]
                out["target_queries"].append({**common, "source_event_id": str(source["event_id"]),
                    "candidate_set_id": "PRIOR_SEED_EVENTS", "claim_status": "RESOLVED",
                    "predicted_target_count": len(best), "confidence": best[0][0]})
                for rank, (score, target) in enumerate(best, 1):
                    out["target_ranks"].append({**common, "source_event_id": str(source["event_id"]),
                        "candidate_set_id": "PRIOR_SEED_EVENTS", "target_rank": rank,
                        "target_event_id": str(target["event_id"]), "target_score": score,
                        "type_id": _hash("t", [prop, source_role, roles[_analysis_key(target)]], 12)})
            likely_operator = representation == "CONSTRUCTION_SPAN" and role_freq[source_role] >= 3 and (
                len(_analysis_tokens(source)) <= 2 or
                str(source.get("separator_after", "")) != str(source.get("separator_before", "")))
            if likely_operator and i + 1 < len(rec_rows):
                start_i = i + 1; end_i = min(len(rec_rows) - 1, i + 4)
                for j in range(i + 1, min(len(rec_rows), i + 7)):
                    if roles[_analysis_key(rec_rows[j])] == source_role:
                        end_i = max(start_i, j - 1); break
                present = True; start_id = str(rec_rows[start_i]["event_id"]); end_id = str(rec_rows[end_i]["event_id"])
                conf = min(.94, .58 + role_freq[source_role] / max(20, len(held_rows)))
            else:
                present = False; start_id = ""; end_id = ""; conf = .64
            if representation == "CONSTRUCTION_SPAN":
                common = _common(source, representation, "PRIMARY", "SCOPE")
                out["scope_claims"].append({**common, "source_event_id": str(source["event_id"]),
                    "claim_status": "RESOLVED", "scope_present": present,
                    "predicted_start_event_id": start_id, "predicted_end_event_id": end_id,
                    "scope_type_id": _hash("q", source_role, 12), "confidence": round(conf, 6)})

    # Architecture rows are per held seed and include the preregistered matched
    # multi-signal and repetition-only variants.
    anchor = held_rows[0]
    for descriptor in classify_world(model) if representation == "MULTI_RESOLUTION" else ():
        variant = descriptor["method_variant"]
        common = _common(anchor, representation, variant, "WORLD_ARCHITECTURE")
        out["architecture_partition_claims"].append({**common, "claim_status": "RESOLVED",
            "architecture_cluster_id": descriptor["cluster"], "confidence": round(.5 + .49 * abs(descriptor["score"] - .5) * 2, 6)})
        for prop in ARCH_FLAGS:
            value, conf = descriptor["flags"][prop]
            common = _common(anchor, representation, variant, prop)
            out["architecture_binary_claims"].append({**common, "claim_status": "RESOLVED",
                "predicted_bool": bool(value), "confidence": round(min(.99, conf), 6)})
    return out
