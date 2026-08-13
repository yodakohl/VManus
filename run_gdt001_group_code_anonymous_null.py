#!/usr/bin/env python3
"""Frequency-optimized anonymous 27-state matched null for the Czech group code."""

import hashlib, json, math

import numpy as np

from gdt001_core import ROOT, canonical, categorical_bits, fixed_costs, load_lattice
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_character_code import encoded


def cpu(counts, maps):
    output = []
    for mapping in maps:
        groups = [[] for _ in range(27)]
        for source, target in enumerate(mapping): groups[int(target)].append(int(counts[source]))
        totals = [sum(group) for group in groups]
        value = categorical_bits(totals) + sum(categorical_bits(group) for group in groups if group)
        output.append(value)
    return np.asarray(output)


def gpu(counts_np, maps):
    import torch
    counts = torch.as_tensor(counts_np, device="cuda", dtype=torch.float64); output = []
    constants = torch.lgamma(counts + .5) - torch.lgamma(torch.tensor(.5, device="cuda", dtype=torch.float64))
    for start in range(0, len(maps), 512):
        mapping = torch.as_tensor(maps[start:start + 512], device="cuda"); n = len(mapping)
        totals = torch.zeros((n, 27), device="cuda", dtype=torch.float64); members = torch.zeros_like(totals); multiplicity = torch.zeros_like(totals)
        totals.scatter_add_(1, mapping, counts.expand(n, -1)); members.scatter_add_(1, mapping, constants.expand(n, -1)); multiplicity.scatter_add_(1, mapping, torch.ones_like(mapping, dtype=torch.float64))
        # Integrated 27-state unigram stream.
        latent = torch.lgamma(totals.sum(1) + 13.5) - torch.lgamma(torch.tensor(13.5, device="cuda", dtype=torch.float64))
        latent -= (torch.lgamma(totals + .5) - torch.lgamma(torch.tensor(.5, device="cuda", dtype=torch.float64))).sum(1)
        # Integrated source identity conditional on each occupied state.
        reverse_logp = torch.lgamma(.5 * multiplicity) - torch.lgamma(totals + .5 * multiplicity) + members
        reverse = -torch.where(multiplicity > 0, reverse_logp, 0).sum(1)
        output.append(((latent + reverse) / math.log(2)).cpu().numpy())
    return np.concatenate(output)


def search(counts, seed, population=8192, generations=30):
    rng = np.random.default_rng(seed); k = len(counts); pop = rng.integers(0, 27, size=(population, k), dtype=np.int64)
    for _ in range(generations):
        scores = gpu(counts, pop); elite = pop[np.argsort(scores)[:256]].copy(); children = elite[rng.integers(0, len(elite), population - len(elite))].copy()
        rows = np.arange(len(children)); positions = rng.integers(0, k, len(children)); children[rows, positions] = rng.integers(0, 27, len(children)); pop = np.vstack([elite, children])
    scores = gpu(counts, pop); index = int(np.argmin(scores)); mapping = pop[index].copy()
    # Exact best coordinate closure.
    current = float(scores[index])
    for _ in range(k * 2):
        candidates = np.repeat(mapping[None, :], k * 26, axis=0); row = 0
        for position, old in enumerate(mapping):
            for target in range(27):
                if target != old: candidates[row, position] = target; row += 1
        values = gpu(counts, candidates); best = int(np.argmin(values))
        if float(values[best]) >= current - 1e-9: break
        mapping = candidates[best].copy(); current = float(values[best])
    exact = float(cpu(counts, mapping[None, :])[0]); assert abs(exact - current) < 2e-6
    return exact, mapping


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    _, counts, _, vocab, _, common = encoded(paths, 512)
    scale = json.loads((ROOT / "gdt001_group_code_scale_stability.json").read_text()); language = min(scale["rows"], key=lambda row: row["total_bits"])
    rows = []
    for seed in (38101, 38102, 38103):
        payload, mapping = search(counts, seed); key = language["key_bits"] - math.log2(5); total = fixed + key + payload
        mapping_rows = [{"source_group": vocab[i], "state": f"STATE_{int(target):02d}", "occurrences": int(counts[i])} for i, target in enumerate(mapping)]
        rows.append({"seed": seed, "total_bits": total, "bits_per_symbol": total / sum(len(word) for path in paths for word in path.words),
                     "gap_vs_best_czech_bits": total - language["total_bits"], "key_bits": key, "payload_bits": payload, "fixed_bits": fixed,
                     "decoder_hash": hashlib.sha256(canonical(mapping_rows)).hexdigest(), "mapping": mapping_rows, "cpu_exact": True})
    best = min(rows, key=lambda row: row["total_bits"]); decision = "STOP_CZECH_ANONYMOUS_NULL_WINS" if best["gap_vs_best_czech_bits"] < 0 else "CONTINUE_CZECH_BEATS_ANONYMOUS_NULL"
    output = {"schema": "GDT001_GROUP_CODE_ANONYMOUS_NULL_V1", "status": "EXPLORATORY_CONTROL", "decision": decision, "best": best, "rows": rows,
              "claim_ceiling": "Matched anonymous-state control only; no state is an established character, sound, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_group_code_anonymous_null_results.json").write_bytes(canonical(output)); print(json.dumps({"decision": decision, "best": {k:v for k,v in best.items() if k != "mapping"}}))


if __name__ == "__main__": main()
