#!/usr/bin/env python3
"""Refit the sparse context/metadata source family to frozen controls."""

import csv, hashlib, json, math, random
from collections import Counter, defaultdict

from gdt001_controls import CONTROL_NAMES, seed_for, transform
from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_context_axis_source import AXES, bits, counts
from run_gdt001_source_selected_nulls import encoded


def identity_rare_symbols(seed=9401):
    alphabet = list(LETTERS); permuted = list(alphabet)
    random.Random(seed_for("BOUNDARY_PRESERVING_IDENTITY_PERMUTATION", "GLOBAL", seed)).shuffle(permuted)
    mapping = dict(zip(alphabet, permuted)); return "".join(sorted(mapping[c] for c in "juz"))


def fit(lines, paths, rare_symbols):
    fixed = sum(fixed_costs(paths).values()); symbols = sum(len(w) for p in paths for w in p.words)
    nulls = frozenset(rare_symbols); seqs, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1
    rare_key = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
    order = 2; global_counts, split = counts(lines, seqs, alphabet, order); contexts = sorted(global_counts)
    base = sum(bits(global_counts[c], alphabet) for c in contexts); options = []
    for ctx in contexts:
        gcost = bits(global_counts[ctx], alphabet); candidates = []
        for axis, _ in AXES:
            cost = sum(bits(counter, alphabet) for counter in split[axis][ctx].values())
            candidates.append((gcost - cost, axis))
        gain, axis = max(candidates, key=lambda x: (x[0], x[1])); options.append((gain, ctx, axis))
    options.sort(key=lambda x: (-x[0], x[1], x[2])); n = len(options); cumulative = 0.0; best = None
    for k in range(n + 1):
        if k: cumulative += options[k - 1][0]
        subset = universal_uint_bits(k) + (math.log2(math.comb(n, k)) if 0 < k < n else 0.0) + k * math.log2(len(AXES))
        key = 3.0 + math.log2(3) + rare_key + subset; payload = base - cumulative
        candidate = (fixed + side + key + payload, k, key, payload)
        if best is None or candidate < best: best = candidate
    total, k, key, payload = best
    global_key = 3.0 + math.log2(3) + rare_key + universal_uint_bits(0)
    global_total = fixed + side + global_key + base
    return {"selected_contexts": k, "available_contexts": n, "total_bits": total,
            "bits_per_symbol": total / symbols, "matched_global_bits": global_total,
            "gain_vs_matched_global_bits": global_total - total, "key_bits": key,
            "payload_bits": payload, "side_channel_bits": side, "fixed_bits": fixed,
            "rare_symbols": rare_symbols, "source_symbols": symbols, "cpu_exact": True}


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); rows = []
    real = fit(lines, paths, "juz"); rows.append({"manuscript": "REAL", **real})
    for control in CONTROL_NAMES:
        changed = transform(lines, paths, control)
        rare = identity_rare_symbols() if control == "BOUNDARY_PRESERVING_IDENTITY_PERMUTATION" else "juz"
        rows.append({"manuscript": control, **fit(lines, changed, rare)})
    best_control = max(row["gain_vs_matched_global_bits"] for row in rows[1:])
    decision = "CONTINUE_REAL_SPECIFIC_CONTEXT_AXIS" if real["gain_vs_matched_global_bits"] > best_control else "STOP_CONTROL_MATCHES_REAL"
    result = {"schema": "GDT001_CONTEXT_AXIS_CONTROLS_V1", "status": "EXPLORATORY_CONTROL",
              "decision": decision, "real": rows[0], "controls": rows[1:],
              "claim_ceiling": "Counterfactual source-compression specificity only; no language, cipher, meaning, or plaintext follows."}
    (ROOT / "gdt001_context_axis_control_results.json").write_bytes(canonical(result))
    with (ROOT / "gdt001_context_axis_control_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "real_gain": real["gain_vs_matched_global_bits"], "best_control_gain": best_control,
                      "rows": [(r["manuscript"], round(r["gain_vs_matched_global_bits"], 1)) for r in rows]}))


if __name__ == "__main__":
    main()
