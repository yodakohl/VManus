#!/usr/bin/env python3
"""GPU best-improvement refinement of the closest whole-group language key."""

import hashlib, json, math

import numpy as np

from gdt001_core import ROOT, canonical, fixed_costs, load_lattice
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_character_code import encoded
from run_gdt001_group_code_high_order import cpu, dense_costs, gpu, lm, sufficient


def ids(rows):
    return np.asarray([26 if row["target"] == " " else ord(row["target"]) - 97 for row in rows], dtype=np.int64)


def mapping_rows(mapping, vocab, counts):
    return [{"source_group": vocab[i], "target": " " if target == 26 else chr(97 + int(target)),
             "occurrences": int(counts[i])} for i, target in enumerate(mapping)]


def refine(costs, keys, freq, counts, initial, order, seed):
    rng = np.random.default_rng(seed); current = initial.copy()
    current_bits = float(cpu(costs, keys, freq, counts, current[None, :], order)[0]); trajectory = [current_bits]
    # Alternate exact best one-coordinate closure with deterministic random
    # two-coordinate barrier probes.
    for barrier_round in range(9):
        for coordinate_round in range(256):
            candidates = np.repeat(current[None, :], len(current) * 26, axis=0)
            row = 0
            for position, old in enumerate(current):
                for target in range(27):
                    if target != old:
                        candidates[row, position] = target; row += 1
            scores = gpu(costs, keys, freq, counts, candidates, order); best = int(np.argmin(scores))
            if float(scores[best]) >= current_bits - 1e-9: break
            current = candidates[best].copy(); current_bits = float(scores[best]); trajectory.append(current_bits)
        if barrier_round == 8: break
        candidates = np.repeat(current[None, :], 8192, axis=0)
        positions = rng.integers(0, len(current), size=(len(candidates), 2))
        targets = rng.integers(0, 27, size=(len(candidates), 2))
        rr = np.arange(len(candidates)); candidates[rr, positions[:, 0]] = targets[:, 0]; candidates[rr, positions[:, 1]] = targets[:, 1]
        scores = gpu(costs, keys, freq, counts, candidates, order); best = int(np.argmin(scores))
        if float(scores[best]) < current_bits - 1e-9:
            current = candidates[best].copy(); current_bits = float(scores[best]); trajectory.append(current_bits)
    exact = float(cpu(costs, keys, freq, counts, current[None, :], order)[0])
    assert abs(exact - current_bits) < 2e-6
    return current, exact, trajectory


def main():
    order = 4; language = "medieval_czech"; k = 128
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(word) for path in paths for word in path.words)
    seqs, counts, _, vocab, _, _ = encoded(paths, k); keys, freq = sufficient(seqs, order, k)
    costs = dense_costs(lm(language, order), order)
    base = json.loads((ROOT / "gdt001_group_code_high_order_results.json").read_text())
    mapping_artifact = json.loads((ROOT / "gdt001_group_code_high_order_mappings.json").read_text())
    starts = [item for item in mapping_artifact["mappings"] if item["language"] == language and item["order"] == order]
    null_total = next(row["total_bits"] for row in base["rows"] if row["model"] == "MATCHED_GROUP_NULL" and row["order"] == order)
    leader_total = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]["total_bits"]
    rows = []
    for item in starts:
        mapping, payload, trajectory = refine(costs, keys, freq, counts, ids(item["mapping"]), order, int(item["seed"]))
        mr = mapping_rows(mapping, vocab, counts); total = fixed + item["key_bits"] + payload
        rows.append({"seed": item["seed"], "language": language, "order": order, "k": k, "initial_total_bits": item["total_bits"],
                     "total_bits": total, "bits_per_symbol": total / symbols, "gap_vs_matched_null_bits": total - null_total,
                     "gap_vs_variable_context_bits": total - leader_total, "key_bits": item["key_bits"], "payload_bits": payload,
                     "fixed_bits": fixed, "accepted_moves": len(trajectory) - 1, "decoder_hash": hashlib.sha256(canonical(mr)).hexdigest(),
                     "mapping": mr, "cpu_exact": True})
    best = min(rows, key=lambda row: row["total_bits"])
    decision = ("CONTINUE" if best["gap_vs_matched_null_bits"] < 0 else "STOP") + "_ORDER4_REFINED_" + ("STABLE" if len({r["decoder_hash"] for r in rows}) == 1 else "UNSTABLE")
    output = {"schema": "GDT001_GROUP_CODE_ORDER4_REFINE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "decision": decision,
              "best": best, "rows": rows, "claim_ceiling": "Search refinement only; no group has an established character, sound, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_group_code_order4_refine_results.json").write_bytes(canonical(output))
    print(json.dumps({"decision": decision, "best": {key: value for key, value in best.items() if key != "mapping"}}))


if __name__ == "__main__": main()
