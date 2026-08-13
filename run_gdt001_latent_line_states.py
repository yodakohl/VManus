#!/usr/bin/env python3
"""GPU-proposed, CPU-exact anonymous latent line-state source mixture."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

import numpy as np
import torch

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


KS = (1, 2, 4, 6, 8, 12, 16, 24, 32)
SEEDS = tuple(range(28101, 28109))


def line_features(seqs, alphabet, order=2):
    shape = (alphabet + 1, alphabet + 1, alphabet); dim = int(np.prod(shape)); rows = []
    for seq in seqs:
        vector = np.zeros(dim, dtype=np.float32); history = [alphabet, alphabet]
        for token in seq:
            vector[np.ravel_multi_index((history[0], history[1], token), shape)] += 1
            history = [history[1], token]
        rows.append(vector)
    return np.stack(rows), shape


def propose(x, k, seed, iterations=40):
    if k == 1: return np.zeros(len(x), dtype=np.int64)
    torch.manual_seed(seed); device = torch.device("cuda"); data = torch.as_tensor(x, device=device)
    generator = torch.Generator(device=device); generator.manual_seed(seed)
    assign = torch.randint(k, (len(x),), generator=generator, device=device)
    for _ in range(iterations):
        tables = torch.zeros((k, x.shape[1]), dtype=torch.float32, device=device)
        tables.index_add_(0, assign, data); denominators = tables.reshape(k, -1, 23).sum(dim=2, keepdim=True)
        costs = -torch.log2((tables.reshape(k, -1, 23) + .5) / (denominators + 11.5)).reshape(k, -1)
        scores = data @ costs.T
        priors = -torch.log2((torch.bincount(assign, minlength=k).float() + .5) / (len(x) + .5 * k))
        new_assign = torch.argmin(scores + priors, dim=1)
        if torch.equal(new_assign, assign): break
        assign = new_assign
    return assign.cpu().numpy()


def exact_score(seqs, assignments, k, alphabet):
    state_counts = Counter(map(int, assignments)); emission = defaultdict(Counter)
    for seq, state in zip(seqs, assignments):
        history = [alphabet, alphabet]
        for token in seq:
            emission[(int(state), tuple(history))][token] += 1; history = [history[1], token]
    assignment_bits = categorical_bits([state_counts[i] for i in range(k)])
    emission_bits = sum(categorical_bits([counter.get(i, 0) for i in range(alphabet)]) for counter in emission.values())
    return assignment_bits, emission_bits, state_counts, emission


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words)
    source = json.loads((ROOT / "gdt001_source_selected_null_results.json").read_text())["selected_source_null"]
    leader = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())["best"]
    nulls = frozenset(source["null_symbols"]); seqs, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1
    rare_key = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
    x, shape = line_features(seqs, alphabet); rows = []; assignments_out = []
    for k in KS:
        seeds = (0,) if k == 1 else SEEDS
        for seed in seeds:
            assignments = propose(x, k, seed); used = sorted(set(map(int, assignments)))
            # Canonicalize label symmetry by first occurrence.
            renumber = {}; canon = []
            for state in map(int, assignments):
                if state not in renumber: renumber[state] = len(renumber)
                canon.append(renumber[state])
            assignments = np.asarray(canon, dtype=np.int64); effective_k = len(renumber)
            assignment_bits, emission_bits, state_counts, emission = exact_score(seqs, assignments, effective_k, alphabet)
            key = 3.0 + math.log2(len(KS)) + rare_key + universal_uint_bits(effective_k) + universal_uint_bits(2)
            total = fixed + side + key + assignment_bits + emission_bits
            decoder = {"schema": "GDT001_LATENT_LINE_STATE_DECODER_V1", "requested_k": k, "effective_k": effective_k,
                       "order": 2, "rare_symbols": source["null_symbols"], "state_counts": dict(sorted(state_counts.items())),
                       "reconstruction": "decode one anonymous state per physical line, then decode the line-reset state-specific KT character process and ordered rare-sign channel"}
            digest = hashlib.sha256(canonical(decoder | {"assignments": assignments.tolist()})).hexdigest()
            row = {"requested_k": k, "effective_k": effective_k, "seed": seed, "total_bits": total,
                   "bits_per_symbol": total / symbols, "gap_vs_context_axis_bits": total - leader["total_bits"],
                   "gap_vs_source_winner_bits": total - source["total_bits"], "key_bits": key,
                   "state_assignment_bits": assignment_bits, "emission_bits": emission_bits,
                   "side_channel_bits": side, "fixed_bits": fixed, "decoder_hash": digest,
                   "gpu_proposal": k > 1, "cpu_exact": True}
            rows.append(row); assignments_out.append({"requested_k": k, "effective_k": effective_k, "seed": seed,
                                                       "decoder_hash": digest, "assignments": assignments.tolist()})
    best = min(rows, key=lambda r: r["total_bits"]); same = [r for r in rows if r["requested_k"] == best["requested_k"]]
    stable = len({r["decoder_hash"] for r in same}) == 1
    decision = ("CONTINUE" if best["gap_vs_context_axis_bits"] < 0 else "STOP") + "_LATENT_LINE_STATES_" + ("STABLE" if stable else "UNSTABLE")
    result = {"schema": "GDT001_LATENT_LINE_STATES_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": best, "rows": rows, "cuda": str(torch.cuda.get_device_name(0)),
              "claim_ceiling": "Exploratory anonymous line-generator states only; no state has a document role, word, syntax, language, cipher, or meaning."}
    (ROOT / "gdt001_latent_line_state_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_latent_line_state_assignments.json").write_bytes(canonical({"schema": "GDT001_LATENT_LINE_STATE_ASSIGNMENTS_V1", "runs": assignments_out}))
    with (ROOT / "gdt001_latent_line_state_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best, "cuda": result["cuda"]}))


if __name__ == "__main__":
    main()
