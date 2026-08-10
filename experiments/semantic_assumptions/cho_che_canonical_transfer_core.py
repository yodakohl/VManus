#!/usr/bin/env python3
"""Target-agnostic scorer for the CCT001 canonical-transfer experiment."""
from __future__ import annotations

import hashlib
import math
from collections import Counter, defaultdict

READINGS = ("ZL3b", "IT2a", "RF1b")
LEAVES = ("f39", "f55", "f68", "f73", "f87", "f89", "f90", "f96")
SCOPES = ("CONFIRMED_PROSE", "DIAGNOSTIC_NONPROSE")
PREFIXES = ("ch", "sh")


class ContractError(ValueError):
    pass


def _freq_bin(n: int) -> int:
    if n <= 0:
        raise ContractError("nonpositive type frequency")
    return n.bit_length() - 1


def validate_masked_geometry(rows: list[dict]) -> None:
    forbidden = {"raw_type", "canonical_type", "realization", "surface", "template", "score", "effect", "p_value"}
    if len(rows) != 2223 or len({r["source_group_id"] for r in rows}) != len(rows):
        raise ContractError("masked row identity/count")
    if set(rows[0]) & forbidden:
        raise ContractError("target-valued masked column")
    if {r["edition"] for r in rows} != set(READINGS) or {r["physical_folio"] for r in rows} != set(LEAVES):
        raise ContractError("reading/leaf geometry")
    cells = Counter((r["edition"], r["physical_folio"], r["side"]) for r in rows)
    if len(cells) != 48 or min(cells.values()) < 8 or {r["side"] for r in rows} != {"r", "v"}:
        raise ContractError("side geometry")
    for r in rows:
        if r["page_state"] not in {"0", "1"} or r["site_prefix"] not in PREFIXES:
            raise ContractError("masked state/prefix")


def validate_events(events: list[dict]) -> dict:
    if not events or len({e["event_id"] for e in events}) != len(events):
        raise ContractError("duplicate/empty event IDs")
    required = {"event_id", "edition", "leaf", "side", "state", "scope", "prefix", "raw_type", "canonical_type", "realization", "length", "site_index"}
    meta = {}
    by_canon = defaultdict(dict)
    counts = Counter()
    for e in events:
        if set(e) != required:
            raise ContractError("event schema")
        if e["edition"] not in READINGS or e["leaf"] not in LEAVES or e["side"] not in {"r", "v"} or e["state"] not in (0, 1):
            raise ContractError("event geometry")
        if e["scope"] not in SCOPES or e["prefix"] not in PREFIXES or e["realization"] not in {"o", "e"}:
            raise ContractError("event class")
        if not isinstance(e["length"], int) or not isinstance(e["site_index"], int) or not (0 <= e["site_index"] < e["length"]):
            raise ContractError("event position")
        m = (e["canonical_type"], e["realization"], e["prefix"], e["length"], e["site_index"])
        old = meta.setdefault(e["raw_type"], m)
        if old != m:
            raise ContractError("inconsistent raw-type metadata")
        old_raw = by_canon[e["canonical_type"]].setdefault(e["realization"], e["raw_type"])
        if old_raw != e["raw_type"]:
            raise ContractError("multiple raw types per canonical realization")
        counts[e["raw_type"]] += 1
    if {e["edition"] for e in events} != set(READINGS) or {e["leaf"] for e in events} != set(LEAVES):
        raise ContractError("missing readings/leaves")
    pairs = []
    for canonical, members in by_canon.items():
        if set(members) == {"o", "e"}:
            o, q = members["o"], members["e"]
            mo, me = meta[o], meta[q]
            if mo[0] != canonical or me[0] != canonical or mo[2:] != me[2:]:
                raise ContractError("broken canonical pair")
            shell = (mo[3], mo[2], mo[4], _freq_bin(counts[o]), _freq_bin(counts[q]))
            pairs.append({"canonical": canonical, "o": o, "e": q, "shell": shell})
        elif not set(members) <= {"o", "e"}:
            raise ContractError("canonical realization")
    pairs.sort(key=lambda p: (p["shell"], p["o"], p["e"]))
    shells = defaultdict(list)
    for p in pairs:
        shells[p["shell"]].append(p)
    movable = sum(len(v) for v in shells.values() if len(v) >= 2)
    pair_types = {p[k] for p in pairs for k in ("o", "e")}
    pair_events = [e for e in events if e["raw_type"] in pair_types]
    capacity = {
        "collision_pairs": len(pairs),
        "movable_pairs": movable,
        "collision_events": len(pair_events),
        "collision_event_fraction": len(pair_events) / len(events),
        "pair_event_leaves": sorted({e["leaf"] for e in pair_events}),
        "pair_event_readings": sorted({e["edition"] for e in pair_events}),
    }
    capacity["passes"] = len(pairs) >= 24 and movable >= 16 and set(capacity["pair_event_leaves"]) == set(LEAVES) and set(capacity["pair_event_readings"]) == set(READINGS)
    return {"pairs": pairs, "shells": dict(shells), "meta": meta, "counts": counts, "capacity": capacity}


def _assigned_state(e: dict, flips: dict[str, int]) -> int:
    return e["state"] ^ flips[e["leaf"]]


def _gain_table(events: list[dict], inv: dict, flips: dict[str, int], *, editions=None, eval_leaves=None, excluded_leaves=None, scope=None, prefix=None) -> dict[tuple[str, str], float]:
    editions = set(READINGS if editions is None else editions)
    eval_leaves = set(LEAVES if eval_leaves is None else eval_leaves)
    excluded = set(() if excluded_leaves is None else excluded_leaves)
    base = [e for e in events if e["edition"] in editions and e["leaf"] not in excluded and (scope is None or e["scope"] == scope) and (prefix is None or e["prefix"] == prefix)]
    contexts = [(r, f) for r in READINGS if r in editions for f in LEAVES if f in eval_leaves and f not in excluded and any(e["edition"] == r and e["leaf"] == f for e in base)]
    if not contexts:
        return {}
    mates = defaultdict(list)
    for shell in inv["shells"].values():
        os = [p["o"] for p in shell]
        es = [p["e"] for p in shell]
        for o in os:
            mates[o] = es
        for q in es:
            mates[q] = os
    gain = defaultdict(float)
    context_weight = 1.0 / len(contexts)
    for reading, held in contexts:
        evaluation = [e for e in base if e["edition"] == reading and e["leaf"] == held]
        event_weight = context_weight / len(evaluation)
        training = [e for e in base if e["edition"] == reading and e["leaf"] != held]
        presence = {0: set(), 1: set()}
        for e in training:
            presence[_assigned_state(e, flips)].add(e["raw_type"])
        for e in evaluation:
            opposite = 1 - _assigned_state(e, flips)
            seen = presence[opposite]
            t = e["raw_type"]
            if t in seen:
                continue
            for mate in mates.get(t, ()):
                if mate in seen:
                    key = (t, mate) if e["realization"] == "o" else (mate, t)
                    gain[key] += event_weight
    return dict(gain)


def _candidate_gain(table: dict, pairs: list[dict]) -> float:
    return sum(table.get((p["o"], p["e"]), 0.0) for p in pairs)


def _candidate_context_gains(events: list[dict], inv: dict, flips: dict[str, int], *, editions=None, eval_leaves=None, excluded_leaves=None, scope=None, prefix=None) -> dict[tuple[str, str], float]:
    editions = set(READINGS if editions is None else editions)
    eval_leaves = set(LEAVES if eval_leaves is None else eval_leaves)
    excluded = set(() if excluded_leaves is None else excluded_leaves)
    base = [e for e in events if e["edition"] in editions and e["leaf"] not in excluded and (scope is None or e["scope"] == scope) and (prefix is None or e["prefix"] == prefix)]
    mate = {}
    for p in inv["pairs"]:
        mate[p["o"]] = p["e"]
        mate[p["e"]] = p["o"]
    out = {}
    for reading in READINGS:
        if reading not in editions:
            continue
        training_reading = [e for e in base if e["edition"] == reading]
        for held in LEAVES:
            if held not in eval_leaves or held in excluded:
                continue
            evaluation = [e for e in training_reading if e["leaf"] == held]
            if not evaluation:
                continue
            presence = {0: set(), 1: set()}
            for e in training_reading:
                if e["leaf"] != held:
                    presence[_assigned_state(e, flips)].add(e["raw_type"])
            hits = 0
            for e in evaluation:
                seen = presence[1 - _assigned_state(e, flips)]
                t = e["raw_type"]
                hits += t not in seen and mate.get(t) in seen
            out[(reading, held)] = hits / len(evaluation)
    return out


def _reading_from_context(context: dict[tuple[str, str], float]) -> dict[str, float]:
    out = {}
    for reading in READINGS:
        values = [v for (r, _), v in context.items() if r == reading]
        if values:
            out[reading] = sum(values) / len(values)
    return out


def _reading_gains(events, inv, flips, **kwargs):
    return _reading_from_context(_candidate_context_gains(events, inv, flips, **kwargs))


def _primary(reading_gains: dict[str, float]) -> float:
    if set(reading_gains) != set(READINGS):
        raise ContractError("incomplete reading score")
    return sum(reading_gains.values()) / len(READINGS)


def _null_pairings(inv: dict, draws: int = 8192):
    shells = sorted(inv["shells"].items(), key=lambda x: repr(x[0]))
    for draw in range(draws):
        mapping = []
        for shell_key, pairs in shells:
            os = sorted(p["o"] for p in pairs)
            es = sorted((p["e"] for p in pairs), key=lambda q: hashlib.sha256(f"CCT001|MERGE|{draw}|{shell_key!r}|{q}".encode()).digest())
            mapping.extend(zip(os, es))
        yield mapping


def score_world(events: list[dict], *, merge_draws: int = 8192) -> dict:
    inv = validate_events(events)
    zero = {f: 0 for f in LEAVES}
    capacity = inv["capacity"]
    if not capacity["passes"]:
        return {"status": "STOP_INSUFFICIENT_COLLISION_CAPACITY", "capacity": capacity, "passes": False}
    observed_context = _candidate_context_gains(events, inv, zero)
    reading = _reading_from_context(observed_context)
    observed = _primary(reading)
    orbit = []
    orbit_reading = {r: [] for r in READINGS}
    orbit_context = {(r, f): [] for r in READINGS for f in LEAVES}
    for bits in range(256):
        flips = {f: (bits >> i) & 1 for i, f in enumerate(LEAVES)}
        context = _candidate_context_gains(events, inv, flips)
        rg = _reading_from_context(context)
        orbit.append(_primary(rg))
        for r in READINGS:
            orbit_reading[r].append(rg[r])
        for key, value in context.items():
            orbit_context[key].append(value)
    p_state = sum(x >= observed - 1e-15 for x in orbit) / 256.0
    state_excess = observed - sum(orbit) / len(orbit)
    reading_excess = {r: reading[r] - sum(orbit_reading[r]) / len(orbit_reading[r]) for r in READINGS}
    reading_tables = {r: _gain_table(events, inv, zero, editions=(r,)) for r in READINGS}
    null_scores = []
    for mapping in _null_pairings(inv, merge_draws):
        null_scores.append(sum(sum(reading_tables[r].get(pair, 0.0) for pair in mapping) for r in READINGS) / 3.0)
    null_mean = sum(null_scores) / len(null_scores)
    p_merge = (1 + sum(x >= observed - 1e-15 for x in null_scores)) / (len(null_scores) + 1)
    leaf_excess = {r: {f: observed_context[(r, f)] - sum(orbit_context[(r, f)]) / len(orbit_context[(r, f)]) for f in LEAVES} for r in READINGS}
    folio_excess = {f: sum(leaf_excess[r][f] for r in READINGS) / 3.0 for f in LEAVES}
    total_positive = sum(max(0.0, x) for x in folio_excess.values())
    concentration = max((max(0.0, x) for x in folio_excess.values()), default=0.0) / total_positive if total_positive else 1.0
    loo = {}
    for deleted in LEAVES:
        observed_loo = _primary(_reading_gains(events, inv, zero, excluded_leaves=(deleted,)))
        null_loo = []
        for bits in range(256):
            flips = {f: (bits >> i) & 1 for i, f in enumerate(LEAVES)}
            null_loo.append(_primary(_reading_gains(events, inv, flips, excluded_leaves=(deleted,))))
        loo[deleted] = observed_loo - sum(null_loo) / len(null_loo)
    scope = {}
    for s in SCOPES:
        available = sorted({e["leaf"] for e in events if e["scope"] == s})
        obs_context = _candidate_context_gains(events, inv, zero, scope=s)
        obs_reading = _reading_from_context(obs_context)
        null_reading = {r: [] for r in READINGS}
        null_context = {key: [] for key in obs_context}
        for bits in range(256):
            flips = {f: (bits >> i) & 1 for i, f in enumerate(LEAVES)}
            ctx = _candidate_context_gains(events, inv, flips, scope=s)
            rg = _reading_from_context(ctx)
            for r in READINGS:
                null_reading[r].append(rg[r])
            for key, value in ctx.items():
                null_context[key].append(value)
        scope_leaf_excess = {r: {f: obs_context[(r, f)] - sum(null_context[(r, f)]) / len(null_context[(r, f)]) for f in available} for r in READINGS}
        scope[s] = {"reading_excess": {r: obs_reading[r] - sum(null_reading[r]) / len(null_reading[r]) for r in READINGS}, "leaf_state_excess": scope_leaf_excess}
        scope[s]["aggregate_state_excess"] = sum(scope[s]["reading_excess"].values()) / 3.0
        scope[s]["available_leaves"] = available
        scope[s]["positive_leaf_support"] = {r: sum(scope_leaf_excess[r][f] > 1e-15 for f in available) for r in READINGS}
        scope[s]["positive_aggregate_leaf_support"] = sum(sum(scope_leaf_excess[r][f] for r in READINGS) / 3.0 > 1e-15 for f in available)
    prefix = {}
    for p in PREFIXES:
        obs = _reading_gains(events, inv, zero, prefix=p)
        null = {r: [] for r in READINGS}
        for bits in range(256):
            flips = {f: (bits >> i) & 1 for i, f in enumerate(LEAVES)}
            rg = _reading_gains(events, inv, flips, prefix=p)
            for r in READINGS:
                null[r].append(rg[r])
        prefix[p] = {r: obs[r] - sum(null[r]) / len(null[r]) for r in READINGS}
    gates = {
        "capacity": capacity["passes"],
        "primary_state_excess": state_excess >= 0.05 - 1e-15,
        "matched_merge_advantage": observed - null_mean >= 0.03 - 1e-15,
        "state_orbit_p": p_state <= 0.01 + 1e-15,
        "merger_null_p": p_merge <= 0.01 + 1e-15,
        "reading_state_excess": all(v >= 0.02 - 1e-15 for v in reading_excess.values()),
        "leaf_support": sum(x > 1e-15 for x in folio_excess.values()) >= 6 and all(sum(x > 1e-15 for x in leaf_excess[r].values()) >= 4 for r in READINGS),
        "loo_gain": min(loo.values()) >= 0.03 - 1e-15,
        "concentration": concentration <= 0.30 + 1e-15,
        "prose_state_excess": scope["CONFIRMED_PROSE"]["aggregate_state_excess"] >= 0.03 - 1e-15 and all(v > 1e-15 for v in scope["CONFIRMED_PROSE"]["reading_excess"].values()),
        "prose_support": scope["CONFIRMED_PROSE"]["positive_aggregate_leaf_support"] >= 5,
        "diagnostic_state_excess": scope["DIAGNOSTIC_NONPROSE"]["aggregate_state_excess"] >= 0.03 - 1e-15 and all(v > 1e-15 for v in scope["DIAGNOSTIC_NONPROSE"]["reading_excess"].values()),
        "diagnostic_support": scope["DIAGNOSTIC_NONPROSE"]["positive_aggregate_leaf_support"] >= 2,
        "prefix_gain": all(sum(prefix[p].values()) / 3.0 >= 0.02 - 1e-15 and all(v > 1e-15 for v in prefix[p].values()) for p in PREFIXES),
    }
    passes = all(gates.values())
    return {
        "status": "PASS_GENERAL_CANONICAL_TRANSFER" if passes else "NONCONFIRM_GENERAL_CANONICAL_TRANSFER",
        "passes": passes,
        "capacity": capacity,
        "primary_gain": observed,
        "primary_state_excess": state_excess,
        "reading_gains": reading,
        "reading_state_excess": reading_excess,
        "state_orbit_p": p_state,
        "state_orbit": orbit,
        "merge_null_mean": null_mean,
        "merge_null_p": p_merge,
        "merge_null_min": min(null_scores),
        "merge_null_max": max(null_scores),
        "matched_merge_advantage": observed - null_mean,
        "leaf_state_excess": leaf_excess,
        "folio_state_excess": folio_excess,
        "concentration": concentration,
        "leave_one_folio_out": loo,
        "scope": scope,
        "prefix": prefix,
        "gates": gates,
    }


def complement_states(events: list[dict]) -> list[dict]:
    return [{**e, "state": 1 - e["state"]} for e in events]


def compact_score(x: dict) -> dict:
    if "gates" not in x:
        return x
    return {k: x[k] for k in ("status", "passes", "capacity", "primary_gain", "primary_state_excess", "reading_gains", "reading_state_excess", "state_orbit_p", "merge_null_mean", "merge_null_p", "matched_merge_advantage", "leaf_state_excess", "folio_state_excess", "concentration", "leave_one_folio_out", "scope", "prefix", "gates")}
