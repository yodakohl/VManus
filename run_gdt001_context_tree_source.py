#!/usr/bin/env python3
"""Exact MDL variable-order context-tree source generator."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


DEPTHS = tuple(range(7))


def fit_tree(seqs, alphabet, depth):
    counts = defaultdict(Counter); bos = alphabet
    for seq in seqs:
        history = [bos] * depth
        for token in seq:
            for d in range(depth + 1): counts[tuple(reversed(history[-d:])) if d else ()][token] += 1
            if depth: history = history[1:] + [token]
    children_by_parent = defaultdict(list)
    for context in counts:
        if context: children_by_parent[context[:-1]].append(context)
    for parent in children_by_parent: children_by_parent[parent].sort()
    memo = {}; choice = {}
    def solve(context):
        if context in memo: return memo[context]
        leaf = categorical_bits([counts[context].get(i, 0) for i in range(alphabet)])
        if len(context) == depth:
            memo[context] = leaf; choice[context] = "LEAF"; return leaf
        children = children_by_parent.get(context, ())
        split = sum(solve(child) for child in children)
        if 1.0 + leaf <= 1.0 + split:
            memo[context] = 1.0 + leaf; choice[context] = "LEAF"
        else:
            memo[context] = 1.0 + split; choice[context] = "SPLIT"
        return memo[context]
    payload = solve(()); leaves = []
    def collect(context):
        if choice[context] == "LEAF":
            leaves.append({"history_recent_first": list(context),
                           "counts": [counts[context].get(i, 0) for i in range(alphabet)],
                           "bits": categorical_bits([counts[context].get(i, 0) for i in range(alphabet)])})
        else:
            for child in children_by_parent.get(context, ()): collect(child)
    collect(())
    return payload, leaves, sum(v == "SPLIT" for v in choice.values()), sum(v == "LEAF" for v in choice.values())


def score(paths, variant, depth):
    source = json.loads((ROOT / "gdt001_source_selected_null_results.json").read_text())["selected_source_null"]
    if variant == "RARE_CHANNEL":
        nulls = frozenset(source["null_symbols"]); seqs, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1
        identity = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
        alphabet_text = "".join(active) + " "
    else:
        seqs = [p.source_ids for p in paths]; side = identity = 0.0; alphabet = len(LETTERS) + 1; alphabet_text = LETTERS + " "
    payload, leaves, splits, leaf_count = fit_tree(seqs, alphabet, depth)
    key = 3.0 + math.log2(2) + math.log2(len(DEPTHS)) + universal_uint_bits(depth) + identity
    fixed = sum(fixed_costs(paths).values()); total = fixed + key + side + payload
    decoder = {"schema": "GDT001_CONTEXT_TREE_SOURCE_DECODER_V1", "variant": variant, "maximum_depth": depth,
               "alphabet": alphabet_text, "bos_index": alphabet, "rare_symbols": source["null_symbols"] if variant == "RARE_CHANNEL" else "",
               "split_nodes": splits, "leaf_nodes": leaf_count, "leaves": leaves,
               "tree_code": "one stop/split bit at every visited node below maximum depth; fixed alphabet-labelled branches",
               "reconstruction": "line-reset variable-order KT tree emits source stream; ordered rare-event channel restores rare signs"}
    digest = hashlib.sha256(canonical(decoder)).hexdigest(); symbols = sum(len(w) for p in paths for w in p.words)
    return {"variant": variant, "maximum_depth": depth, "split_nodes": splits, "leaf_nodes": leaf_count,
            "total_bits": total, "bits_per_symbol": total / symbols, "key_bits": key,
            "side_channel_bits": side, "payload_bits": payload, "fixed_bits": fixed,
            "decoder_hash": digest, "cpu_exact": True}, decoder


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines)
    old = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]
    rows = []; decoders = []
    for variant in ("RAW", "RARE_CHANNEL"):
        for depth in DEPTHS:
            row, decoder = score(paths, variant, depth); row["gap_vs_variable_context_bits"] = row["total_bits"] - old["total_bits"]
            rows.append(row); decoders.append(decoder | {"decoder_hash": row["decoder_hash"]})
    best = min(rows, key=lambda r: r["total_bits"])
    decision = ("CONTINUE" if best["gap_vs_variable_context_bits"] < 0 else "STOP") + "_CONTEXT_TREE_SOURCE"
    result = {"schema": "GDT001_CONTEXT_TREE_SOURCE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": best, "rows": rows,
              "claim_ceiling": "Exploratory variable-order source generator only; tree histories are not words, language, cipher, meaning, plaintext, or translation."}
    (ROOT / "gdt001_context_tree_source_results.json").write_bytes(canonical(result))
    best_decoder = next(d for d in decoders if d["decoder_hash"] == best["decoder_hash"])
    (ROOT / "gdt001_context_tree_source_decoder.json").write_bytes(canonical(best_decoder))
    with (ROOT / "gdt001_context_tree_source_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__":
    main()
