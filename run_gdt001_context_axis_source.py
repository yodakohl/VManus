#!/usr/bin/env python3
"""Sparse per-context choice among known metadata axes."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


AXES = (("CURRIER", "currier"), ("SECTION", "section"), ("HAND", "hand"),
        ("KIND", "kind"), ("GRAMMAR_SCOPE", "grammar_scope"))


def counts(lines, seqs, alphabet, order):
    global_counts = defaultdict(Counter)
    split = {name: defaultdict(lambda: defaultdict(Counter)) for name, _ in AXES}
    for line, seq in zip(lines, seqs):
        hist = [alphabet] * order
        for token in seq:
            ctx = tuple(hist); global_counts[ctx][token] += 1
            for name, field in AXES: split[name][ctx][getattr(line, field) or "_"][token] += 1
            if order: hist = hist[1:] + [token]
    return global_counts, split


def bits(counter, alphabet):
    return categorical_bits([counter.get(i, 0) for i in range(alphabet)])


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words)
    source = json.loads((ROOT / "gdt001_source_selected_null_results.json").read_text())["selected_source_null"]
    sparse = json.loads((ROOT / "gdt001_sparse_metadata_source_results.json").read_text())["best"]
    nulls = frozenset(source["null_symbols"]); seqs, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1
    rare_key = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
    rows = []; codebooks = []
    for order in (1, 2, 3):
        global_counts, split = counts(lines, seqs, alphabet, order); contexts = sorted(global_counts)
        base = sum(bits(global_counts[c], alphabet) for c in contexts); options = []
        for ctx in contexts:
            global_cost = bits(global_counts[ctx], alphabet); candidates = []
            for axis, _ in AXES:
                cost = sum(bits(counter, alphabet) for counter in split[axis][ctx].values())
                candidates.append((global_cost - cost, axis, cost))
            gain, axis, cost = max(candidates, key=lambda x: (x[0], x[1]))
            options.append((gain, ctx, axis, cost))
        options.sort(key=lambda x: (-x[0], x[1], x[2])); n = len(options); cumulative = 0.0; best = None
        for k in range(n + 1):
            if k: cumulative += options[k - 1][0]
            selection = universal_uint_bits(k) + (math.log2(math.comb(n, k)) if 0 < k < n else 0.0) + k * math.log2(len(AXES))
            key = 3.0 + math.log2(3) + rare_key + selection
            payload = base - cumulative; total = fixed + side + key + payload
            candidate = (total, k, key, payload)
            if best is None or candidate < best: best = candidate
        total, k, key, payload = best; selected = options[:k]
        decoder = {
            "schema": "GDT001_CONTEXT_AXIS_SOURCE_DECODER_V1", "order": order,
            "alphabet": "".join(active) + " ", "rare_symbols": source["null_symbols"],
            "available_axes": [axis for axis, _ in AXES], "global_context_count": n,
            "selected_contexts": [{"context": list(ctx), "axis": axis, "gross_split_gain_bits": gain,
                                   "metadata_values": sorted(split[axis][ctx]),
                                   "counts_by_value": {value: [split[axis][ctx][value].get(i, 0) for i in range(alphabet)] for value in sorted(split[axis][ctx])}}
                                  for gain, ctx, axis, _ in selected],
            "global_counts": {"|".join(map(str, ctx)): [global_counts[ctx].get(i, 0) for i in range(alphabet)] for ctx in contexts},
            "reconstruction": "unlisted contexts use global KT counts; selected contexts use the explicitly named metadata axis and counts; the ordered rare-event channel restores rare signs",
        }
        digest = hashlib.sha256(canonical(decoder)).hexdigest()
        row = {"order": order, "selected_contexts": k, "available_contexts": n,
               "axis_counts": json.dumps(dict(sorted(Counter(x[2] for x in selected).items())), sort_keys=True, separators=(",", ":")),
               "total_bits": total, "bits_per_symbol": total / symbols,
               "gap_vs_sparse_currier_bits": total - sparse["total_bits"],
               "gap_vs_source_winner_bits": total - source["total_bits"], "key_bits": key,
               "side_channel_bits": side, "payload_bits": payload, "fixed_bits": fixed,
               "decoder_hash": digest, "cpu_exact": True}
        rows.append(row); codebooks.append(decoder | {"decoder_hash": digest})
    winner = min(rows, key=lambda x: x["total_bits"])
    decision = ("CONTINUE" if winner["gap_vs_sparse_currier_bits"] < 0 else "STOP") + "_CONTEXT_AXIS_SOURCE"
    result = {"schema": "GDT001_CONTEXT_AXIS_SOURCE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": winner, "rows": rows,
              "claim_ceiling": "Exploratory sparse metadata-conditioned source model; anonymous contexts and metadata axes have no lexical or semantic interpretation."}
    (ROOT / "gdt001_context_axis_source_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_context_axis_source_codebooks.json").write_bytes(canonical({"schema": "GDT001_CONTEXT_AXIS_SOURCE_CODEBOOKS_V1", "codebooks": codebooks}))
    with (ROOT / "gdt001_context_axis_source_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": winner}))


if __name__ == "__main__":
    main()
