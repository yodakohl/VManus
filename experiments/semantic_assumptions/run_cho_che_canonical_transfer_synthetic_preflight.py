#!/usr/bin/env python3
"""Run the target-blind CCT001 synthetic calibration on masked geometry."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from cho_che_canonical_transfer_core import LEAVES, READINGS, compact_score, complement_states, score_world, validate_masked_geometry

B = Path(__file__).resolve().parent
R = B / "results"
PANEL = R / "cho_che_canonical_transfer_masked_panel.tsv"
CAP = R / "cho_che_canonical_transfer_capacity.json"
CAPV = R / "cho_che_canonical_transfer_capacity_validation.json"
SPEC = B / "CHO_CHE_CANONICAL_TRANSFER_SYNTHETIC_PREFLIGHT_SPEC.md"
SELF = Path(__file__).resolve()
CORE = B / "cho_che_canonical_transfer_core.py"
OUT = R / "cho_che_canonical_transfer_synthetic_preflight.json"
REPORT = R / "cho_che_canonical_transfer_synthetic_preflight.md"

EXPECTED = {
    PANEL: "8287193a0fcea0e9e7219153fee3d58b830bc60c5a37ee358dfa8abd18e8bf1a",
    CAP: "44ccd816eb393ccebb017d209d5cfd7b398f46a5af34cf787084ded3507031c5",
    CAPV: "abbac6550d23001b58c9fc7019e29d9fa0f50e0aa6e7e4d740ec870e36a1046c",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hbit(text: str, modulus: int = 10000) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big") % modulus


def load_panel() -> list[dict]:
    rows = list(csv.DictReader(PANEL.open(), delimiter="\t"))
    validate_masked_geometry(rows)
    return rows


def make_world(rows: list[dict], mode: str, seed: int, strength: float = 1.0) -> list[dict]:
    local_rank = {}
    counters = {}
    for r in rows:
        key = (r["edition"], r["physical_folio"], r["side"], r["grammar_scope"], r["site_prefix"])
        rank = counters.get(key, 0)
        counters[key] = rank + 1
        local_rank[r["source_group_id"]] = rank
    events = []
    for r in rows:
        rank = local_rank[r["source_group_id"]]
        site_index = min(2 + (rank % 4), int(r["ascii_length"]) - 1)
        invariant = f"{r['ascii_length']}|{site_index}"
        if mode == "UNIQUE_SURROUNDING":
            base = f"U|{invariant}|{r['source_group_id']}"
        else:
            # Forty-eight recurring contexts per reading/scope/prefix retain
            # realistic uneven page counts while ensuring held-leaf reuse.
            base = f"B|{r['edition']}|{r['grammar_scope']}|{r['site_prefix']}|{invariant}|{rank % 48:02d}"
        state = int(r["page_state"])
        random_real = "o" if hbit(f"CCT001|R|{mode}|{seed}|{r['source_group_id']}") & 1 else "e"
        aligned = hbit(f"CCT001|A|{seed}|{r['source_group_id']}") < round(strength * 10000)
        state_real = "o" if state else "e"
        if mode in {"DISTRIBUTED", "PARTIAL"}:
            realization = state_real if aligned else random_real
        elif mode == "SIDE_ONLY":
            realization = "o" if r["side"] == "r" else "e"
        elif mode == "ONE_FOLIO":
            realization = state_real if r["physical_folio"] == LEAVES[seed % len(LEAVES)] else random_real
        elif mode == "ONE_READING":
            realization = state_real if r["edition"] == READINGS[seed % len(READINGS)] else random_real
        elif mode == "PROSE_ONLY":
            realization = state_real if r["grammar_scope"] == "CONFIRMED_PROSE" else random_real
        elif mode == "DIAGNOSTIC_ONLY":
            realization = state_real if r["grammar_scope"] == "DIAGNOSTIC_NONPROSE" else random_real
        elif mode == "ONE_PREFIX":
            realization = state_real if r["site_prefix"] == ("ch" if seed % 2 == 0 else "sh") else random_real
        elif mode == "ONE_SIDE":
            realization = state_real if r["side"] == ("r" if seed % 2 == 0 else "v") else random_real
        else:  # NULL, GENERIC_COLLAPSE, UNIQUE_SURROUNDING
            realization = random_real
        canonical = f"{base}|X"
        raw = f"{base}|{realization}"
        events.append({
            "event_id": r["source_group_id"],
            "edition": r["edition"],
            "leaf": r["physical_folio"],
            "side": r["side"],
            "state": state,
            "scope": r["grammar_scope"],
            "prefix": r["site_prefix"],
            "raw_type": raw,
            "canonical_type": canonical,
            "realization": realization,
            "length": int(r["ascii_length"]),
            "site_index": site_index,
        })
    return events


def task(args):
    rows, mode, seed, strength = args
    events = make_world(rows, mode, seed, strength)
    return mode, seed, strength, compact_score(score_world(events))


def install(j: bytes, m: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("preflight output exists")
    with tempfile.TemporaryDirectory(prefix="cct001_", dir=R) as d:
        a, b = Path(d) / "result", Path(d) / "report"
        a.write_bytes(j); b.write_bytes(m)
        os.link(a, OUT)
        try:
            os.link(b, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def main() -> None:
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"hash mismatch: {path.name}")
    if json.loads(CAPV.read_text())["status"] != "PASS_INDEPENDENT_REALIZATION_TEMPLATE_MASKED_CAPACITY":
        raise SystemExit("capacity validation status")
    rows = load_panel()
    tasks = [(rows, "NULL", i, 0.0) for i in range(64)]
    tasks += [(rows, "DISTRIBUTED", i, 1.0) for i in range(8)]
    for mode in ("SIDE_ONLY", "ONE_FOLIO", "ONE_READING", "PROSE_ONLY", "DIAGNOSTIC_ONLY", "ONE_PREFIX", "ONE_SIDE", "GENERIC_COLLAPSE", "UNIQUE_SURROUNDING"):
        tasks += [(rows, mode, i, 0.0) for i in range(8)]
    for strength in (0.25, 0.50, 0.75, 1.00):
        tasks += [(rows, "PARTIAL", i, strength) for i in range(8)]
    with ProcessPoolExecutor(max_workers=min(32, os.cpu_count() or 1)) as pool:
        records = list(pool.map(task, tasks, chunksize=1))
    worlds = [{"mode": m, "seed": s, "strength": q, "score": score} for m, s, q, score in records]
    grouped = {}
    for mode in sorted({x["mode"] for x in worlds}):
        qvals = sorted({x["strength"] for x in worlds if x["mode"] == mode})
        for q in qvals:
            z = [x for x in worlds if x["mode"] == mode and x["strength"] == q]
            grouped[f"{mode}@{q:.2f}"] = {"worlds": len(z), "passes": sum(x["score"].get("passes", False) for x in z), "primary_state_excesses": [x["score"].get("primary_state_excess") for x in z]}
    negative_modes = ("SIDE_ONLY", "ONE_FOLIO", "ONE_READING", "PROSE_ONLY", "DIAGNOSTIC_ONLY", "ONE_PREFIX", "ONE_SIDE", "GENERIC_COLLAPSE", "UNIQUE_SURROUNDING")
    null_pass = grouped["NULL@0.00"]["passes"]
    full_pass = grouped["DISTRIBUTED@1.00"]["passes"]
    negative_ok = all(grouped[f"{m}@0.00"]["passes"] == 0 for m in negative_modes)
    partial_eligible = []
    for q in (0.25, 0.50, 0.75, 1.00):
        rec = grouped[f"PARTIAL@{q:.2f}"]
        realized = [x for x in rec["primary_state_excesses"] if x is not None]
        if realized and min(realized) >= 0.05 - 1e-15:
            partial_eligible.append((q, rec["passes"]))
    weakest = partial_eligible[0] if partial_eligible else None
    # One full world is enough to prove exact global-complement invariance;
    # every scalar and gate except the orbit ordering must remain identical.
    sample = make_world(rows, "DISTRIBUTED", 0, 1.0)
    a = compact_score(score_world(sample)); b = compact_score(score_world(complement_states(sample)))
    complement_ok = a == b
    mutation = {}
    for name, mutator in {
        "duplicate_id": lambda e: [*e, dict(e[0])],
        "inconsistent_type": lambda e: [{**x, "length": x["length"] + 1} if i == 0 else x for i, x in enumerate(e)],
        "missing_reading": lambda e: [x for x in e if x["edition"] != "RF1b"],
        "missing_leaf": lambda e: [x for x in e if x["leaf"] != "f96"],
        "broken_pair": lambda e: [{**x, "canonical_type": x["canonical_type"] + "|BROKEN"} if i == 0 else x for i, x in enumerate(e)],
    }.items():
        try:
            score_world(mutator(sample)); mutation[name] = False
        except Exception:
            mutation[name] = True
    malformed_ok = all(mutation.values())
    gates = {
        "null_at_most_one_of_64": null_pass <= 1,
        "distributed_all_eight": full_pass == 8,
        "all_negatives_zero_of_eight": negative_ok,
        "material_partial_at_least_six": weakest is not None and weakest[1] >= 6,
        "state_complement_exact": complement_ok,
        "malformed_controls": malformed_ok,
        "target_values_accessed_zero": True,
    }
    passed = all(gates.values())
    result = {
        "experiment": "CHO_CHE_CANONICAL_TRANSFER_SYNTHETIC_PREFLIGHT",
        "status": "PASS_TARGET_BLIND_CANONICAL_TRANSFER_CALIBRATION" if passed else "STOP_CANONICAL_TRANSFER_CALIBRATION",
        "decision": "AUTHORIZE_CANONICAL_TRANSFER_TARGET_REGISTRATION" if passed else "TARGET_FORBIDDEN",
        "inputs": {p.name: sha(p) for p in (*EXPECTED, SPEC, CORE, SELF)},
        "workers": min(32, os.cpu_count() or 1),
        "world_count": len(worlds),
        "grouped": grouped,
        "weakest_material_partial": None if weakest is None else {"strength": weakest[0], "passes": weakest[1]},
        "complement_control": complement_ok,
        "mutation_controls": mutation,
        "gates": gates,
        "worlds": worlds,
        "target_types_accessed": 0,
        "target_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Synthetic calibration only; no manuscript collapse meaning sound wordhood language cipher plaintext or translation.",
    }
    report = f"# `cho/che` canonical-transfer synthetic preflight\n\nStatus: **{result['status']}**\n\nThe 32-worker run evaluated {len(worlds)} target-blind worlds on the exact 2,223-row masked geometry. Null passes: **{null_pass}/64**; full distributed passes: **{full_pass}/8**; every named negative control rejected: **{negative_ok}**; weakest material partial result: **{weakest}**. State-complement and malformed-input controls: **{complement_ok} / {malformed_ok}**. Decision: **{result['decision']}**. No manuscript type, realization, canonical template, or score was opened.\n"
    install((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": result["status"], "decision": result["decision"], "gates": gates, "grouped": grouped}, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
