#!/usr/bin/env python3
"""Sparse choice between longer local history and metadata-conditioned source tables."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


PREDICTORS = (("HISTORY3", None), ("CURRIER", "currier"), ("SECTION", "section"),
              ("HAND", "hand"), ("KIND", "kind"), ("GRAMMAR_SCOPE", "grammar_scope"))


def bits(counter, alphabet):
    return categorical_bits([counter.get(i, 0) for i in range(alphabet)])


def fit(lines, paths, rare_symbols="juz"):
    nulls = frozenset(rare_symbols); seqs, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1; bos = alphabet
    global_counts = defaultdict(Counter); split = {name: defaultdict(lambda: defaultdict(Counter)) for name, _ in PREDICTORS}
    for line, seq in zip(lines, seqs):
        history = [bos, bos, bos]
        for token in seq:
            context = tuple(history[-2:]); global_counts[context][token] += 1
            split["HISTORY3"][context][history[-3]][token] += 1
            for name, field in PREDICTORS[1:]: split[name][context][getattr(line, field) or "_"][token] += 1
            history = history[1:] + [token]
    contexts = sorted(global_counts); base = sum(bits(global_counts[c], alphabet) for c in contexts); options = []
    for context in contexts:
        shared = bits(global_counts[context], alphabet); candidates = []
        for name, _ in PREDICTORS:
            separated = sum(bits(counter, alphabet) for counter in split[name][context].values())
            candidates.append((shared - separated, name, separated))
        gain, predictor, separated = max(candidates, key=lambda x: (x[0], x[1])); options.append((gain, context, predictor, separated))
    options.sort(key=lambda x: (-x[0], x[1], x[2])); n = len(options); cumulative = 0.0; candidates = []
    rare_key = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
    for k in range(n + 1):
        if k: cumulative += options[k - 1][0]
        selection = universal_uint_bits(k) + (math.log2(math.comb(n, k)) if 0 < k < n else 0.0) + k * math.log2(len(PREDICTORS))
        key = 3.0 + rare_key + selection; payload = base - cumulative
        total = sum(fixed_costs(paths).values()) + side + key + payload
        candidates.append((total, k, key, payload))
    total, k, key, payload = min(candidates); selected = options[:k]
    decoder = {"schema": "GDT001_VARIABLE_CONTEXT_SOURCE_DECODER_V1", "base_order": 2,
               "predictors": [name for name, _ in PREDICTORS], "rare_symbols": rare_symbols,
               "selected_contexts": [{"context": list(context), "predictor": predictor,
                                      "gross_gain_bits": gain, "split_values": [str(v) for v in sorted(split[predictor][context], key=str)]}
                                     for gain, context, predictor, _ in selected],
               "reconstruction": "unlisted histories use shared order-2 KT counts; listed histories select the explicit third-history-symbol or metadata table; ordered rare channel restores rare signs"}
    digest = hashlib.sha256(canonical(decoder)).hexdigest(); symbols = sum(len(w) for p in paths for w in p.words)
    return {"selected_contexts": k, "available_contexts": n,
            "predictor_counts": json.dumps(dict(sorted(Counter(x[2] for x in selected).items())), sort_keys=True, separators=(",", ":")),
            "total_bits": total, "bits_per_symbol": total / symbols, "key_bits": key,
            "side_channel_bits": side, "payload_bits": payload, "fixed_bits": sum(fixed_costs(paths).values()),
            "decoder_hash": digest, "cpu_exact": True}, decoder


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines)
    old = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())["best"]
    row, decoder = fit(lines, paths); row["gap_vs_context_axis_bits"] = row["total_bits"] - old["total_bits"]
    decision = ("CONTINUE" if row["gap_vs_context_axis_bits"] < 0 else "STOP") + "_VARIABLE_CONTEXT_SOURCE"
    result = {"schema": "GDT001_VARIABLE_CONTEXT_SOURCE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": row,
              "claim_ceiling": "Exploratory variable-context source generator only; no context, metadata value, language, cipher, meaning, or plaintext is established."}
    (ROOT / "gdt001_variable_context_source_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_variable_context_source_decoder.json").write_bytes(canonical(decoder | {"decoder_hash": row["decoder_hash"]}))
    with (ROOT / "gdt001_variable_context_source_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(row), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerow(row)
    print(json.dumps({"decision": decision, "best": row}))


if __name__ == "__main__":
    main()
