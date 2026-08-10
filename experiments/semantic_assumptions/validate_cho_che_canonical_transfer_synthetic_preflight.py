#!/usr/bin/env python3
"""Clean reconstruction of CCT001 calibration; imports no production module."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

B = Path(__file__).resolve().parent
R = B / "results"
SELF = Path(__file__).resolve()
PANEL = R / "cho_che_canonical_transfer_masked_panel.tsv"
PROD = R / "cho_che_canonical_transfer_synthetic_preflight.json"
PREPORT = R / "cho_che_canonical_transfer_synthetic_preflight.md"
SPEC = B / "CHO_CHE_CANONICAL_TRANSFER_SYNTHETIC_PREFLIGHT_SPEC.md"
CORE = B / "cho_che_canonical_transfer_core.py"
RUNNER = B / "run_cho_che_canonical_transfer_synthetic_preflight.py"
OUT = R / "cho_che_canonical_transfer_synthetic_preflight_validation.json"
REPORT = R / "cho_che_canonical_transfer_synthetic_preflight_validation.md"

READINGS = ("ZL3b", "IT2a", "RF1b")
LEAVES = ("f39", "f55", "f68", "f73", "f87", "f89", "f90", "f96")
SCOPES = ("CONFIRMED_PROSE", "DIAGNOSTIC_NONPROSE")
PREFIXES = ("ch", "sh")
EXPECTED = {
    PANEL: "8287193a0fcea0e9e7219153fee3d58b830bc60c5a37ee358dfa8abd18e8bf1a",
    SPEC: "49efc5774535c8ba9f47863c4a7f55e1f7aab35abdd3d1661bb8fda687c14d52",
    CORE: "07d81c1dd9f758a4553e271c11a44ef7819141ac685dc149482225e5aa9bf1ce",
    RUNNER: "09babbe9f19092f6db52081aeb524628cd3b844aac13c564f7e61fa5f6f5124e",
    PROD: "645b75e44d7d320a3545c61cfc7cdcf12f978fdae828c74d2cf01c52ad95ce43",
    PREPORT: "e7790d7bc5213f5746b4be1804fa721a8f0fc7aeba9acfc3c1d93f939fdcf029",
}


class Stop(ValueError):
    pass


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hbit(text: str, modulus: int = 10000) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big") % modulus


def synthesize(rows, mode, seed, strength):
    seen = {}
    rank = {}
    for row in rows:
        key = (row["edition"], row["physical_folio"], row["side"], row["grammar_scope"], row["site_prefix"])
        rank[row["source_group_id"]] = seen.get(key, 0)
        seen[key] = seen.get(key, 0) + 1
    out = []
    for row in rows:
        i = rank[row["source_group_id"]]
        pos = min(2 + i % 4, int(row["ascii_length"]) - 1)
        invariant = f"{row['ascii_length']}|{pos}"
        if mode == "UNIQUE_SURROUNDING":
            base = f"U|{invariant}|{row['source_group_id']}"
        else:
            base = f"B|{row['edition']}|{row['grammar_scope']}|{row['site_prefix']}|{invariant}|{i % 48:02d}"
        state = int(row["page_state"])
        random_r = "o" if hbit(f"CCT001|R|{mode}|{seed}|{row['source_group_id']}") & 1 else "e"
        state_r = "o" if state else "e"
        aligned = hbit(f"CCT001|A|{seed}|{row['source_group_id']}") < round(strength * 10000)
        if mode in {"DISTRIBUTED", "PARTIAL"}: value = state_r if aligned else random_r
        elif mode == "SIDE_ONLY": value = "o" if row["side"] == "r" else "e"
        elif mode == "ONE_FOLIO": value = state_r if row["physical_folio"] == LEAVES[seed % 8] else random_r
        elif mode == "ONE_READING": value = state_r if row["edition"] == READINGS[seed % 3] else random_r
        elif mode == "PROSE_ONLY": value = state_r if row["grammar_scope"] == SCOPES[0] else random_r
        elif mode == "DIAGNOSTIC_ONLY": value = state_r if row["grammar_scope"] == SCOPES[1] else random_r
        elif mode == "ONE_PREFIX": value = state_r if row["site_prefix"] == ("ch" if seed % 2 == 0 else "sh") else random_r
        elif mode == "ONE_SIDE": value = state_r if row["side"] == ("r" if seed % 2 == 0 else "v") else random_r
        else: value = random_r
        out.append({"event_id": row["source_group_id"], "edition": row["edition"], "leaf": row["physical_folio"], "side": row["side"], "state": state, "scope": row["grammar_scope"], "prefix": row["site_prefix"], "raw_type": f"{base}|{value}", "canonical_type": f"{base}|X", "realization": value, "length": int(row["ascii_length"]), "site_index": pos})
    return out


def inventory(events):
    required = {"event_id", "edition", "leaf", "side", "state", "scope", "prefix", "raw_type", "canonical_type", "realization", "length", "site_index"}
    if not events or len({x["event_id"] for x in events}) != len(events): raise Stop("IDs")
    type_meta = {}
    groups = defaultdict(dict)
    frequencies = Counter()
    for x in events:
        if set(x) != required: raise Stop("schema")
        if x["edition"] not in READINGS or x["leaf"] not in LEAVES or x["side"] not in {"r", "v"} or x["state"] not in {0, 1}: raise Stop("geometry")
        if x["scope"] not in SCOPES or x["prefix"] not in PREFIXES or x["realization"] not in {"o", "e"}: raise Stop("class")
        if not isinstance(x["length"], int) or not isinstance(x["site_index"], int) or not 0 <= x["site_index"] < x["length"]: raise Stop("position")
        signature = (x["canonical_type"], x["realization"], x["prefix"], x["length"], x["site_index"])
        if x["raw_type"] in type_meta and type_meta[x["raw_type"]] != signature: raise Stop("type metadata")
        type_meta[x["raw_type"]] = signature
        if x["realization"] in groups[x["canonical_type"]] and groups[x["canonical_type"]][x["realization"]] != x["raw_type"]: raise Stop("canonical member")
        groups[x["canonical_type"]][x["realization"]] = x["raw_type"]
        frequencies[x["raw_type"]] += 1
    if {x["edition"] for x in events} != set(READINGS) or {x["leaf"] for x in events} != set(LEAVES): raise Stop("coverage")
    pairs = []
    shells = defaultdict(list)
    for canonical, members in groups.items():
        if set(members) == {"o", "e"}:
            o, e = members["o"], members["e"]
            a, b = type_meta[o], type_meta[e]
            if a[0] != canonical or b[0] != canonical or a[2:] != b[2:]: raise Stop("pair")
            shell = (a[3], a[2], a[4], frequencies[o].bit_length() - 1, frequencies[e].bit_length() - 1)
            p = {"canonical": canonical, "o": o, "e": e, "shell": shell}
            pairs.append(p); shells[shell].append(p)
    pairs.sort(key=lambda p: (p["shell"], p["o"], p["e"]))
    shells = {k: sorted(v, key=lambda p: (p["shell"], p["o"], p["e"])) for k, v in shells.items()}
    movable = sum(len(v) for v in shells.values() if len(v) >= 2)
    types = {p[k] for p in pairs for k in ("o", "e")}
    pair_events = [x for x in events if x["raw_type"] in types]
    cap = {"collision_pairs": len(pairs), "movable_pairs": movable, "collision_events": len(pair_events), "collision_event_fraction": len(pair_events) / len(events), "pair_event_leaves": sorted({x["leaf"] for x in pair_events}), "pair_event_readings": sorted({x["edition"] for x in pair_events})}
    cap["passes"] = len(pairs) >= 24 and movable >= 16 and set(cap["pair_event_leaves"]) == set(LEAVES) and set(cap["pair_event_readings"]) == set(READINGS)
    return pairs, shells, cap


def state(x, flips): return x["state"] ^ flips[x["leaf"]]


def contexts(events, pairs, flips, editions=None, eval_leaves=None, excluded=None, scope=None, prefix=None):
    editions = set(READINGS if editions is None else editions); eval_leaves = set(LEAVES if eval_leaves is None else eval_leaves); excluded = set(() if excluded is None else excluded)
    data = [x for x in events if x["edition"] in editions and x["leaf"] not in excluded and (scope is None or x["scope"] == scope) and (prefix is None or x["prefix"] == prefix)]
    mate = {}
    for p in pairs: mate[p["o"]] = p["e"]; mate[p["e"]] = p["o"]
    answer = {}
    for reading in READINGS:
        if reading not in editions: continue
        rd = [x for x in data if x["edition"] == reading]
        for leaf in LEAVES:
            if leaf not in eval_leaves or leaf in excluded: continue
            held = [x for x in rd if x["leaf"] == leaf]
            if not held: continue
            present = {0: set(), 1: set()}
            for x in rd:
                if x["leaf"] != leaf: present[state(x, flips)].add(x["raw_type"])
            answer[(reading, leaf)] = sum(x["raw_type"] not in present[1-state(x, flips)] and mate.get(x["raw_type"]) in present[1-state(x, flips)] for x in held) / len(held)
    return answer


def readings(ctx):
    ans = {}
    for r in READINGS:
        v = [x for (q, _), x in ctx.items() if q == r]
        if v: ans[r] = sum(v) / len(v)
    return ans


def primary(rg):
    if set(rg) != set(READINGS): raise Stop("reading score")
    return sum(rg.values()) / 3.0


def allowed_table(events, pairs, shells, flips, reading):
    data = [x for x in events if x["edition"] == reading]
    possible = defaultdict(list)
    for values in shells.values():
        os = [p["o"] for p in values]; es = [p["e"] for p in values]
        for o in os: possible[o] = es
        for e in es: possible[e] = os
    answer = defaultdict(float)
    for leaf in LEAVES:
        held = [x for x in data if x["leaf"] == leaf]
        present = {0: set(), 1: set()}
        for x in data:
            if x["leaf"] != leaf: present[state(x, flips)].add(x["raw_type"])
        weight = 1.0 / 8.0 / len(held)
        for x in held:
            pool = present[1-state(x, flips)]; t = x["raw_type"]
            if t in pool: continue
            for mate in possible.get(t, ()):
                if mate in pool:
                    key = (t, mate) if x["realization"] == "o" else (mate, t)
                    answer[key] += weight
    return answer


def null_maps(shells):
    ordered = sorted(shells.items(), key=lambda x: repr(x[0]))
    for draw in range(8192):
        result = []
        for shell, values in ordered:
            oside = sorted(p["o"] for p in values)
            eside = sorted((p["e"] for p in values), key=lambda x: hashlib.sha256(f"CCT001|MERGE|{draw}|{shell!r}|{x}".encode()).digest())
            result.extend(zip(oside, eside))
        yield result


def evaluate(events):
    pairs, shells, capacity = inventory(events)
    if not capacity["passes"]: return {"status": "STOP_INSUFFICIENT_COLLISION_CAPACITY", "capacity": capacity, "passes": False}
    zero = {f: 0 for f in LEAVES}
    obs_ctx = contexts(events, pairs, zero); obs_reading = readings(obs_ctx); observed = primary(obs_reading)
    orbit = []; orbit_reading = {r: [] for r in READINGS}; orbit_context = {(r, f): [] for r in READINGS for f in LEAVES}
    for bits in range(256):
        flips = {f: bits >> i & 1 for i, f in enumerate(LEAVES)}
        ctx = contexts(events, pairs, flips); rg = readings(ctx)
        orbit.append(primary(rg))
        for r in READINGS: orbit_reading[r].append(rg[r])
        for key, value in ctx.items(): orbit_context[key].append(value)
    p_state = sum(x >= observed - 1e-15 for x in orbit) / 256.0
    state_excess = observed - sum(orbit) / 256.0
    reading_excess = {r: obs_reading[r] - sum(orbit_reading[r]) / 256.0 for r in READINGS}
    tables = {r: allowed_table(events, pairs, shells, zero, r) for r in READINGS}
    null = [sum(sum(tables[r].get(pair, 0.0) for pair in mapping) for r in READINGS) / 3.0 for mapping in null_maps(shells)]
    null_mean = sum(null) / len(null); p_merge = (1 + sum(x >= observed - 1e-15 for x in null)) / (len(null) + 1)
    leaf_excess = {r: {f: obs_ctx[(r, f)] - sum(orbit_context[(r, f)]) / 256.0 for f in LEAVES} for r in READINGS}
    folio_excess = {f: sum(leaf_excess[r][f] for r in READINGS) / 3.0 for f in LEAVES}
    denom = sum(max(0.0, x) for x in folio_excess.values()); concentration = max((max(0.0, x) for x in folio_excess.values()), default=0.0) / denom if denom else 1.0
    loo = {}
    for deleted in LEAVES:
        observed_loo = primary(readings(contexts(events, pairs, zero, excluded=(deleted,))))
        values = []
        for bits in range(256): values.append(primary(readings(contexts(events, pairs, {f: bits >> i & 1 for i, f in enumerate(LEAVES)}, excluded=(deleted,)))))
        loo[deleted] = observed_loo - sum(values) / 256.0
    scope_result = {}
    for scope in SCOPES:
        available = sorted({x["leaf"] for x in events if x["scope"] == scope})
        oc = contexts(events, pairs, zero, scope=scope); rr = readings(oc); nr = {r: [] for r in READINGS}; nc = {key: [] for key in oc}
        for bits in range(256):
            ctx = contexts(events, pairs, {f: bits >> i & 1 for i, f in enumerate(LEAVES)}, scope=scope); rg = readings(ctx)
            for r in READINGS: nr[r].append(rg[r])
            for key, value in ctx.items(): nc[key].append(value)
        lx = {r: {f: oc[(r, f)] - sum(nc[(r, f)]) / 256.0 for f in available} for r in READINGS}
        rx = {r: rr[r] - sum(nr[r]) / 256.0 for r in READINGS}
        scope_result[scope] = {"reading_excess": rx, "leaf_state_excess": lx, "aggregate_state_excess": sum(rx.values()) / 3.0, "available_leaves": available, "positive_leaf_support": {r: sum(lx[r][f] > 1e-15 for f in available) for r in READINGS}, "positive_aggregate_leaf_support": sum(sum(lx[r][f] for r in READINGS) / 3.0 > 1e-15 for f in available)}
    prefix_result = {}
    for prefix in PREFIXES:
        rr = readings(contexts(events, pairs, zero, prefix=prefix)); nr = {r: [] for r in READINGS}
        for bits in range(256):
            rg = readings(contexts(events, pairs, {f: bits >> i & 1 for i, f in enumerate(LEAVES)}, prefix=prefix))
            for r in READINGS: nr[r].append(rg[r])
        prefix_result[prefix] = {r: rr[r] - sum(nr[r]) / 256.0 for r in READINGS}
    gates = {
        "capacity": capacity["passes"], "primary_state_excess": state_excess >= .05 - 1e-15,
        "matched_merge_advantage": observed - null_mean >= .03 - 1e-15, "state_orbit_p": p_state <= .01 + 1e-15, "merger_null_p": p_merge <= .01 + 1e-15,
        "reading_state_excess": all(v >= .02 - 1e-15 for v in reading_excess.values()),
        "leaf_support": sum(x > 1e-15 for x in folio_excess.values()) >= 6 and all(sum(x > 1e-15 for x in leaf_excess[r].values()) >= 4 for r in READINGS),
        "loo_gain": min(loo.values()) >= .03 - 1e-15, "concentration": concentration <= .30 + 1e-15,
        "prose_state_excess": scope_result[SCOPES[0]]["aggregate_state_excess"] >= .03 - 1e-15 and all(v > 1e-15 for v in scope_result[SCOPES[0]]["reading_excess"].values()),
        "prose_support": scope_result[SCOPES[0]]["positive_aggregate_leaf_support"] >= 5,
        "diagnostic_state_excess": scope_result[SCOPES[1]]["aggregate_state_excess"] >= .03 - 1e-15 and all(v > 1e-15 for v in scope_result[SCOPES[1]]["reading_excess"].values()),
        "diagnostic_support": scope_result[SCOPES[1]]["positive_aggregate_leaf_support"] >= 2,
        "prefix_gain": all(sum(prefix_result[p].values()) / 3.0 >= .02 - 1e-15 and all(v > 1e-15 for v in prefix_result[p].values()) for p in PREFIXES),
    }
    passed = all(gates.values())
    return {"status": "PASS_GENERAL_CANONICAL_TRANSFER" if passed else "NONCONFIRM_GENERAL_CANONICAL_TRANSFER", "passes": passed, "capacity": capacity, "primary_gain": observed, "primary_state_excess": state_excess, "reading_gains": obs_reading, "reading_state_excess": reading_excess, "state_orbit_p": p_state, "merge_null_mean": null_mean, "merge_null_p": p_merge, "matched_merge_advantage": observed-null_mean, "leaf_state_excess": leaf_excess, "folio_state_excess": folio_excess, "concentration": concentration, "leave_one_folio_out": loo, "scope": scope_result, "prefix": prefix_result, "gates": gates}


ROWS = None
def init_worker(rows):
    global ROWS; ROWS = rows
def rebuild(record):
    return {"mode": record["mode"], "seed": record["seed"], "strength": record["strength"], "score": evaluate(synthesize(ROWS, record["mode"], record["seed"], record["strength"]))}


def compare(a, b, path="root"):
    checks = 1
    if isinstance(a, float) or isinstance(b, float):
        if a is None or b is None or abs(float(a)-float(b)) > 2e-12: raise AssertionError(f"{path}: {a} != {b}")
    elif type(a) is not type(b): raise AssertionError(f"{path}: type")
    elif isinstance(a, dict):
        if set(a) != set(b): raise AssertionError(f"{path}: keys {set(a)^set(b)}")
        for k in a: checks += compare(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        if len(a) != len(b): raise AssertionError(f"{path}: length")
        for i, (x, y) in enumerate(zip(a, b)): checks += compare(x, y, f"{path}[{i}]")
    elif a != b: raise AssertionError(f"{path}: {a!r} != {b!r}")
    return checks


def install(j, m):
    if OUT.exists() or REPORT.exists(): raise FileExistsError("validation output exists")
    with tempfile.TemporaryDirectory(prefix="cct001v_", dir=R) as d:
        a, b = Path(d)/"j", Path(d)/"m"; a.write_bytes(j); b.write_bytes(m); os.link(a, OUT)
        try: os.link(b, REPORT)
        except Exception: OUT.unlink(missing_ok=True); raise


def main():
    checks = 0
    for p, h in EXPECTED.items():
        if sha(p) != h: raise AssertionError(f"hash {p.name}")
        checks += 1
    production = json.loads(PROD.read_text())
    rows = list(csv.DictReader(PANEL.open(), delimiter="\t"))
    if len(rows) != 2223 or len({x["source_group_id"] for x in rows}) != 2223 or {x["edition"] for x in rows} != set(READINGS) or {x["physical_folio"] for x in rows} != set(LEAVES): raise AssertionError("panel")
    forbidden = {"raw_type","canonical_type","realization","surface","template","score","effect","p_value"}
    if set(rows[0]) & forbidden: raise AssertionError("masked columns")
    checks += 5
    with ProcessPoolExecutor(max_workers=min(32, os.cpu_count() or 1), initializer=init_worker, initargs=(rows,)) as pool:
        rebuilt = list(pool.map(rebuild, production["worlds"], chunksize=1))
    for i, (actual, expected) in enumerate(zip(rebuilt, production["worlds"])): checks += compare(actual, expected, f"worlds[{i}]")
    grouped = {}
    for mode in sorted({x["mode"] for x in rebuilt}):
        for strength in sorted({x["strength"] for x in rebuilt if x["mode"] == mode}):
            z = [x for x in rebuilt if x["mode"] == mode and x["strength"] == strength]
            grouped[f"{mode}@{strength:.2f}"] = {"worlds": len(z), "passes": sum(x["score"].get("passes", False) for x in z), "primary_state_excesses": [x["score"].get("primary_state_excess") for x in z]}
    checks += compare(grouped, production["grouped"], "grouped")
    weakest = next(({"strength": q, "passes": grouped[f"PARTIAL@{q:.2f}"]["passes"]} for q in (.25,.50,.75,1.0) if min(x for x in grouped[f"PARTIAL@{q:.2f}"]["primary_state_excesses"] if x is not None) >= .05-1e-15), None)
    checks += compare(weakest, production["weakest_material_partial"], "weakest")
    sample = synthesize(rows, "DISTRIBUTED", 0, 1.0); complemented = [{**x, "state": 1-x["state"]} for x in sample]
    complement_ok = evaluate(sample) == evaluate(complemented)
    mutations = {}
    mutations["duplicate_id"] = [*sample, dict(sample[0])]
    mutations["inconsistent_type"] = [{**x,"length":x["length"]+1} if i==0 else x for i,x in enumerate(sample)]
    mutations["missing_reading"] = [x for x in sample if x["edition"]!="RF1b"]
    mutations["missing_leaf"] = [x for x in sample if x["leaf"]!="f96"]
    mutations["broken_pair"] = [{**x,"canonical_type":x["canonical_type"]+"|BROKEN"} if i==0 else x for i,x in enumerate(sample)]
    mutation_result = {}
    for name, data in mutations.items():
        try: evaluate(data); mutation_result[name] = False
        except Exception: mutation_result[name] = True
    checks += compare(complement_ok, production["complement_control"], "complement")
    checks += compare(mutation_result, production["mutation_controls"], "mutations")
    gates = {"null_at_most_one_of_64": grouped["NULL@0.00"]["passes"]<=1, "distributed_all_eight": grouped["DISTRIBUTED@1.00"]["passes"]==8, "all_negatives_zero_of_eight": all(grouped[f"{m}@0.00"]["passes"]==0 for m in ("SIDE_ONLY","ONE_FOLIO","ONE_READING","PROSE_ONLY","DIAGNOSTIC_ONLY","ONE_PREFIX","ONE_SIDE","GENERIC_COLLAPSE","UNIQUE_SURROUNDING")), "material_partial_at_least_six": weakest is not None and weakest["passes"]>=6, "state_complement_exact": complement_ok, "malformed_controls": all(mutation_result.values()), "target_values_accessed_zero": True}
    checks += compare(gates, production["gates"], "gates")
    if production["status"] != "PASS_TARGET_BLIND_CANONICAL_TRANSFER_CALIBRATION" or production["decision"] != "AUTHORIZE_CANONICAL_TRANSFER_TARGET_REGISTRATION" or production["target_types_accessed"] or production["target_scores_computed"] or not all(gates.values()): raise AssertionError("decision/access")
    checks += 5
    result = {"experiment":"CHO_CHE_CANONICAL_TRANSFER_SYNTHETIC_PREFLIGHT_VALIDATION", "status":"PASS_INDEPENDENT_176_WORLD_RECONSTRUCTION", "checks_passed":checks, "worlds_reconstructed":len(rebuilt), "inputs":{p.name:sha(p) for p in (*EXPECTED,SELF)}, "grouped":grouped, "gates":gates, "target_types_accessed":0, "target_scores_computed":0, "english_glosses":0, "claim_ceiling":"Target-blind calibration validation only; no manuscript collapse meaning sound wordhood language cipher plaintext or translation."}
    report = f"# `cho/che` canonical-transfer calibration validation\n\n**PASS**: clean code reconstructed all **{len(rebuilt)}** target-blind worlds and {checks:,} schema, numeric, invariance, mutation, gate, and decision checks. Null/full/material-partial: **{grouped['NULL@0.00']['passes']}/64**, **{grouped['DISTRIBUTED@1.00']['passes']}/8**, **{weakest['passes']}/8 at {weakest['strength']:.2f}**. No manuscript type, realization, canonical template, or score was accessed.\n"
    install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode())
    print(json.dumps({"status":result["status"],"checks":checks,"worlds":len(rebuilt),"gates":gates},sort_keys=True))

if __name__ == "__main__": main()
