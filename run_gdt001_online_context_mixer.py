#!/usr/bin/env python3
"""Causal fixed-share mixture of local-history and metadata source experts."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

from gdt001_core import ROOT, LETTERS, canonical, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded
from run_gdt001_variable_context_source import PREDICTORS


SHARES = (0.0, 1 / 4096, 1 / 1024, 1 / 256, 1 / 64, 1 / 16)


def probability(counter, token, alphabet):
    return (counter[token] + .5) / (sum(counter.values()) + .5 * alphabet)


def fit(lines, paths, share, rare_symbols="juz"):
    nulls = frozenset(rare_symbols); sequences, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1; bos = alphabet
    # Every base order-2 history has an independent causal mixture over the
    # seven experts. Counts and posterior weights begin empty/uniform.
    shared = defaultdict(Counter); longer = defaultdict(Counter)
    metadata = {name: defaultdict(Counter) for name, _ in PREDICTORS[1:]}; weights = {}; payload = 0.0; selections = Counter()
    expert_names = ["SHARED", *[name for name, _ in PREDICTORS]]
    for line, sequence in zip(lines, sequences):
        history = [bos, bos, bos]
        for token in sequence:
            context = tuple(history[-2:]); long_key = (context, history[-3])
            counters = [shared[context], longer[long_key]]
            for name, field in PREDICTORS[1:]: counters.append(metadata[name][(context, getattr(line, field) or "_")])
            probs = [probability(counter, token, alphabet) for counter in counters]
            current = weights.setdefault(context, [1 / len(counters)] * len(counters)); mixture = sum(w * p for w, p in zip(current, probs))
            payload -= math.log2(mixture); posterior = [w * p / mixture for w, p in zip(current, probs)]
            weights[context] = [(1 - share) * value + share / len(counters) for value in posterior]
            selections[expert_names[max(range(len(current)), key=lambda i: (current[i], expert_names[i]))]] += 1
            for counter in counters: counter[token] += 1
            history = history[1:] + [token]
    rare_key = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
    # One bit selects this family versus the jointly authorized hidden-state
    # alternative; the six-way share-grid choice is separate.
    key = 3.0 + rare_key + math.log2(2) + math.log2(len(SHARES)); fixed = sum(fixed_costs(paths).values()); total = fixed + side + key + payload
    decoder = {"schema": "GDT001_ONLINE_CONTEXT_MIXER_DECODER_V1", "base_history": 2, "experts": expert_names,
               "share": share, "prior": "uniform independently for every observed order-2 context",
               "prediction": "causal KT-1/2 expert probabilities mixed by pre-event weights",
               "update": "Bayes posterior after each observed source token, then fixed-share toward uniform; all expert counts update causally",
               "serialization_order": "canonical corpus-lattice line order, not asserted physical writing chronology",
               "line_reset": True, "rare_symbols": "juz"}
    return {"share": share, "total_bits": total, "bits_per_symbol": total / sum(len(word) for path in paths for word in path.words),
            "gap_vs_variable_context_bits": total - json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]["total_bits"],
            "key_bits": key, "payload_bits": payload, "side_channel_bits": side, "fixed_bits": fixed,
            "dominant_expert_events": json.dumps(dict(sorted(selections.items())), sort_keys=True, separators=(",", ":")),
            "decoder_hash": hashlib.sha256(canonical(decoder)).hexdigest(), "decoder": decoder, "cpu_exact": True}


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); rows = [fit(lines, paths, share) for share in SHARES]
    best = min(rows, key=lambda row: row["total_bits"]); decision = ("CONTINUE" if best["gap_vs_variable_context_bits"] < 0 else "STOP") + "_ONLINE_CONTEXT_MIXER"
    output = {"schema": "GDT001_ONLINE_CONTEXT_MIXER_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "decision": decision,
              "best": best, "rows": [{key:value for key,value in row.items() if key != "decoder"} for row in rows],
              "claim_ceiling": "Causal source-symbol context mixture only; no expert, metadata field, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_online_context_mixer_results.json").write_bytes(canonical(output))
    with (ROOT / "gdt001_online_context_mixer_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(output["rows"][0]); writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(output["rows"])
    print(json.dumps({"decision": decision, "best": {key:value for key,value in best.items() if key != "decoder"}}))


if __name__ == "__main__": main()
