#!/usr/bin/env python3
"""Target-free controls for F69M001."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from f69m001_core import ALPHABET, evaluate, null_prefix_codes, synthetic_sequences, validate_sequences


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
CAPACITY = RESULTS / "f69m001_capacity.json"
METHOD = BASE / "F69M001_LUNAR_MANSION_PREFIX_METHOD.md"
OUT = RESULTS / "f69m001_controls.json"
REPORT = RESULTS / "f69m001_controls.md"
MODES = ("FULL_PLANT", "NULL", "DOMINANT_INITIAL_ONLY", "FOUR_BLOCK_ONLY", "SHALLOW_TWO_DEPTH_ONLY")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists(): raise SystemExit("refusing overwrite")
    capacity = json.loads(CAPACITY.read_text())
    if capacity["status"] != "PASS_UNSCORED_28_ORDERED_LABELS_AND_FIXED_ROSTER": raise SystemExit("capacity")
    roster = [row["name"] for row in capacity["historical_roster"]]
    nulls = {domain: null_prefix_codes(roster, domain) for domain in ("GLOBAL", "INITIAL_CONDITIONED")}
    records = []
    for world in range(8):
        for mode in MODES:
            result = evaluate(synthetic_sequences(roster, world, mode), roster, nulls)
            records.append({"world": world, "mode": mode, "evaluation": result})
    pass_counts = {mode: sum(r["evaluation"]["passes"] for r in records if r["mode"] == mode) for mode in MODES}

    base_seq = synthetic_sequences(roster, 0, "FULL_PLANT")
    base = evaluate(base_seq, roster, nulls)
    rotated = evaluate(base_seq[5:] + base_seq[:5], roster, nulls)
    reflected = evaluate([base_seq[(-i) % 28] for i in range(28)], roster, nulls)
    relabel = {family: ALPHABET[(index + 9) % 21] for index, family in enumerate(ALPHABET)}
    relabeled = evaluate(["".join(relabel[c] for c in value) for value in base_seq], roster, nulls)
    invariance = {
        "rotation": base["S"] == rotated["S"] and base["p_global"] == rotated["p_global"] and base["p_initial_conditioned"] == rotated["p_initial_conditioned"] and base["passes"] == rotated["passes"],
        "reflection": base["S"] == reflected["S"] and base["p_global"] == reflected["p_global"] and base["p_initial_conditioned"] == reflected["p_initial_conditioned"] and base["passes"] == reflected["passes"],
        "anonymous_family_relabeling": base["S"] == relabeled["S"] and base["p_global"] == relabeled["p_global"] and base["p_initial_conditioned"] == relabeled["p_initial_conditioned"] and base["passes"] == relabeled["passes"],
        "row_serialization": base["sequence_sha256"] == evaluate(list(base_seq), roster, nulls)["sequence_sha256"],
    }
    mutations = {}
    cases = {
        "missing": base_seq[:-1], "duplicate": base_seq + [base_seq[0]],
        "too_short": [*base_seq[:-1], "AA"], "unknown_family": [*base_seq[:-1], "A?A"],
    }
    for name, values in cases.items():
        try: validate_sequences(values)
        except ValueError: mutations[name] = True
        else: mutations[name] = False
    gates = {
        "full_plant_passes_8_of_8": pass_counts["FULL_PLANT"] == 8,
        "null_rejected_8_of_8": pass_counts["NULL"] == 0,
        "dominant_initial_only_rejected_8_of_8": pass_counts["DOMINANT_INITIAL_ONLY"] == 0,
        "four_block_only_rejected_8_of_8": pass_counts["FOUR_BLOCK_ONLY"] == 0,
        "shallow_two_depth_only_rejected_8_of_8": pass_counts["SHALLOW_TWO_DEPTH_ONLY"] == 0,
        "all_invariances": all(invariance.values()), "all_mutations_rejected": all(mutations.values()),
        "no_Voynich_target_prefixes_accessed": True, "zero_English_glosses": True,
    }
    if not all(gates.values()): raise AssertionError({"pass_counts": pass_counts, "invariance": invariance, "mutations": mutations, "gates": gates})
    result = {
        "experiment": "F69M001_TARGET_BLIND_CONTROLS", "status": "PASS_40_WORLD_PREFIX_TOPOLOGY_CONTROLS",
        "inputs": {path.name: sha(path) for path in (CAPACITY, METHOD, BASE / "f69m001_core.py", Path(__file__))},
        "records": records, "pass_counts": pass_counts, "invariance": invariance,
        "mutations_rejected": mutations, "gates": gates,
        "decision": "REQUIRE_INDEPENDENT_RECONSTRUCTION_BEFORE_TARGET_FREEZE",
        "claim_ceiling": "Synthetic prefix-equivalence controls only; no Voynich f69v prefix topology, roster identity, name, sound, meaning, plaintext, or translation was accessed.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# F69M001 target-blind controls\n\nStatus: **PASS_40_WORLD_PREFIX_TOPOLOGY_CONTROLS**\n\n"
        "All eight complete three-depth plants pass. Exact-null, dominant-initial-only, four-name-block-only, "
        "and shallow-two-depth-only fixtures pass 0/8. Rotation, reflection, anonymous relabeling, "
        "serialization, and malformed-input guards pass. No f69v target prefix was opened; independent "
        "reconstruction is required before a hash freeze. No roster identity, word, sound, meaning, "
        "plaintext, or translation follows.\n"
    )
    print(json.dumps({"status": result["status"], "pass_counts": pass_counts}, sort_keys=True))


if __name__ == "__main__": main()
