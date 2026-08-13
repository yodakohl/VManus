#!/usr/bin/env python3
"""Counterfactual specificity of the refined whole-group Czech code."""

import csv, hashlib, json, math, random
from collections import Counter

import numpy as np

from gdt001_controls import CONTROL_NAMES, seed_for, transform
from gdt001_core import ROOT, LETTERS, SOURCE_ALPHABET, canonical, categorical_bits, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_character_code import encoded
from run_gdt001_group_code_high_order import dense_costs, lm, search
from run_gdt001_group_code_order4_refine import ids, mapping_rows, refine, sufficient


def encoded_vocab(paths, vocab):
    k = len(vocab); ix = {word: index for index, word in enumerate(vocab)}; counts = np.zeros(k); seqs = []
    residual = []; lengths = Counter(); modes = Counter()
    for path in paths:
        run = []
        for word in path.words:
            if word in ix:
                token = ix[word]; run.append(token); counts[token] += 1; modes["CODE"] += 1
            else:
                modes["RESIDUAL"] += 1; residual.append(tuple(LETTERS.index(char) for char in word)); lengths[len(word)] += 1
                if run: seqs.append(run); run = []
        if run: seqs.append(run)
    dictionary = universal_uint_bits(k) + sum(universal_uint_bits(len(word)) + len(word) * math.log2(25) for word in vocab)
    maximum = max(lengths, default=0)
    common = dictionary + categorical_bits([modes["CODE"], modes["RESIDUAL"]]) + universal_uint_bits(maximum)
    common += categorical_bits([lengths[n] for n in range(1, maximum + 1)]) + kt_ngram_bits(residual, 25, 2)
    return seqs, counts, vocab, common


def fit(name, paths, costs, initial=None, seed=35101, vocab_override=None):
    k = 128; order = 4
    fixed = sum(fixed_costs(paths).values()); symbols = sum(len(word) for path in paths for word in path.words)
    if vocab_override is None:
        seqs, counts, _, vocab, _, common = encoded(paths, k)
    else:
        seqs, counts, vocab, common = encoded_vocab(paths, vocab_override)
    keys, freq = sufficient(seqs, order, k)
    null_payload = kt_ngram_bits(seqs, k, order)
    null_key = 3.0 + math.log2(1) + math.log2(2) + universal_uint_bits(order) + common
    null_total = fixed + null_key + null_payload
    if initial is None:
        _, initial = search(costs, seqs, counts, k, order, seed, population=4096, generations=14)
    mapping, payload, trajectory = refine(costs, keys, freq, counts, initial, order, seed)
    key = 3.0 + math.log2(1) + math.log2(2) + math.log2(5) + universal_uint_bits(order) + common + k * math.log2(27)
    total = fixed + key + payload; mr = mapping_rows(mapping, vocab, counts)
    return {"manuscript": name, "total_bits": total, "bits_per_symbol": total / symbols,
            "matched_null_bits": null_total, "gain_vs_matched_null_bits": null_total - total,
            "key_bits": key, "payload_bits": payload, "fixed_bits": fixed, "source_symbols": symbols,
            "accepted_refinement_moves": len(trajectory) - 1,
            "decoder_hash": hashlib.sha256(canonical(mr)).hexdigest(), "cpu_exact": True}


def main():
    _, lines = load_lattice(); real_paths = common_selected_paths(lines); costs = dense_costs(lm("medieval_czech", 4), 4)
    refined = json.loads((ROOT / "gdt001_group_code_order4_refine_results.json").read_text())
    initial_real = ids(refined["best"]["mapping"])
    _, _, _, real_vocab, _, _ = encoded(real_paths, 128)
    rows = [fit("REAL", real_paths, costs, initial_real, 35101, real_vocab)]
    for name in CONTROL_NAMES:
        changed = transform(lines, real_paths, name)
        if name == "BOUNDARY_PRESERVING_IDENTITY_PERMUTATION":
            alphabet = list(SOURCE_ALPHABET[:-1]); permuted = list(alphabet)
            random.Random(seed_for(name, "GLOBAL", 9401)).shuffle(permuted); rename = dict(zip(alphabet, permuted))
            transformed_vocab = ["".join(rename[char] for char in word) for word in real_vocab]
            rows.append(fit(name, changed, costs, initial_real, 35101, transformed_vocab))
        else:
            rows.append(fit(name, changed, costs, None, 35101))
    controls = rows[1:]; larger = [row for row in controls if row["gain_vs_matched_null_bits"] >= rows[0]["gain_vs_matched_null_bits"] - 1e-9]
    decision = "CONTINUE_REAL_SPECIFIC_GROUP_LANGUAGE" if not larger else "STOP_CONTROLS_MATCH_GROUP_LANGUAGE"
    output = {"schema": "GDT001_GROUP_CODE_ORDER4_CONTROLS_V1", "status": "EXPLORATORY_CONTROL", "decision": decision,
              "real": rows[0], "controls": controls, "controls_matching_or_exceeding_real": [row["manuscript"] for row in larger],
              "claim_ceiling": "Counterfactual specificity of an anonymous complete-group code only; no established character, sound, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_group_code_order4_control_results.json").write_bytes(canonical(output))
    with (ROOT / "gdt001_group_code_order4_control_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "rows": [(row["manuscript"], round(row["gain_vs_matched_null_bits"], 3)) for row in rows]}))


if __name__ == "__main__": main()
