#!/usr/bin/env python3
"""Frequent construction roots as latent Czech characters with explicit affix reconstruction."""

import hashlib, json, math
from collections import Counter

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_record_models import PREFIXES, SUFFIXES, decompose
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_code_high_order import dense_costs, lm, search, sufficient
from run_gdt001_group_code_order4_refine import mapping_rows, refine


def encode(paths, k):
    counts = Counter(decompose(word)[1] for path in paths for word in path.words)
    vocab = [root for root, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:k]]; index = {root: i for i, root in enumerate(vocab)}
    sequences = []; code_counts = [0] * k; residual = []; residual_lengths = Counter(); prefixes = Counter(); suffixes = Counter(); modes = Counter()
    for path in paths:
        run = []
        for word in path.words:
            prefix, root, suffix = decompose(word); prefixes[prefix or "_"] += 1; suffixes[suffix or "_"] += 1
            if root in index:
                token = index[root]; run.append(token); code_counts[token] += 1; modes["CODE"] += 1
            else:
                residual.append(tuple(LETTERS.index(char) for char in root)); residual_lengths[len(root)] += 1; modes["RESIDUAL"] += 1
                if run: sequences.append(run); run = []
        if run: sequences.append(run)
    maximum = max(residual_lengths, default=0)
    dictionary = universal_uint_bits(k) + sum(universal_uint_bits(len(root)) + len(root) * math.log2(len(LETTERS)) for root in vocab)
    common = dictionary + categorical_bits([modes["CODE"], modes["RESIDUAL"]]) + universal_uint_bits(maximum)
    common += categorical_bits([residual_lengths[n] for n in range(1, maximum + 1)]) + kt_ngram_bits(residual, len(LETTERS), 2)
    common += categorical_bits([prefixes[key] for key in ("_", *PREFIXES)]) + categorical_bits([suffixes[key] for key in ("_", *SUFFIXES)])
    return sequences, __import__('numpy').asarray(code_counts), vocab, common


def main():
    k = 256; order = 4; language = "medieval_czech"; seed = 37101
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values()); symbols = sum(len(word) for path in paths for word in path.words)
    sequences, counts, vocab, common = encode(paths, k); costs = dense_costs(lm(language, order), order)
    _, initial = search(costs, sequences, counts, k, order, seed); keys, frequency = sufficient(sequences, order, k)
    mapping, payload, trajectory = refine(costs, keys, frequency, counts, initial, order, seed)
    null_payload = kt_ngram_bits(sequences, k, order); null_key = 3.0 + universal_uint_bits(order) + common
    key = null_key + math.log2(5) + k * math.log2(27); null_total = fixed + null_key + null_payload; total = fixed + key + payload
    rows = mapping_rows(mapping, vocab, counts); leader = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]["total_bits"]
    result = {"schema": "GDT001_ROOT_CHARACTER_CODE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": ("CONTINUE" if total < null_total else "STOP") + "_ROOT_CHARACTER_SINGLE_RESTART",
              "result": {"k": k, "order": order, "language": language, "seed": seed, "total_bits": total, "bits_per_symbol": total / symbols,
                         "matched_null_bits": null_total, "gain_vs_matched_null_bits": null_total - total, "gap_vs_variable_context_bits": total - leader,
                         "key_bits": key, "payload_bits": payload, "fixed_bits": fixed, "coded_events": int(counts.sum()), "coded_runs": len(sequences),
                         "runs_length_at_least_5": sum(len(seq) >= 5 for seq in sequences), "accepted_refinement_moves": len(trajectory) - 1,
                         "decoder_hash": hashlib.sha256(canonical(rows)).hexdigest(), "mapping": rows, "cpu_exact": True},
              "claim_ceiling": "Construction-root character-code diagnostic only; no root has an established character, sound, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_root_character_code_results.json").write_bytes(canonical(result)); print(json.dumps({"decision": result["decision"], "result": {k:v for k,v in result["result"].items() if k != "mapping"}}))


if __name__ == "__main__": main()
