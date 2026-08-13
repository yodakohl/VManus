#!/usr/bin/env python3
"""Sparse metadata-specific exceptions to a shared source character process."""

import csv, hashlib, itertools, json, math
from collections import Counter, defaultdict

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


AXES = (("CURRIER", "currier"), ("SECTION", "section"), ("HAND", "hand"),
        ("KIND", "kind"), ("CODE", "code"), ("GRAMMAR_SCOPE", "grammar_scope"),
        ("PAGE", "page"))


def context_counts(lines, seqs, field, alphabet, order):
    global_counts = defaultdict(Counter); split_counts = defaultdict(lambda: defaultdict(Counter)); bos = alphabet
    for line, seq in zip(lines, seqs):
        value = getattr(line, field) or "_"; history = [bos] * order
        for token in seq:
            ctx = tuple(history); global_counts[ctx][token] += 1; split_counts[ctx][value][token] += 1
            if order: history = history[1:] + [token]
    return global_counts, split_counts


def c_bits(counter, alphabet):
    return categorical_bits([counter.get(i, 0) for i in range(alphabet)])


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words)
    old = json.loads((ROOT / "gdt001_metadata_conditioned_source_results.json").read_text())["best"]
    source = json.loads((ROOT / "gdt001_source_selected_null_results.json").read_text())["selected_source_null"]
    nulls = frozenset(source["null_symbols"]); seqs, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1
    rare_key = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
    rows = []; codebooks = []
    for axis_name, field in AXES:
        for order in (1, 2, 3):
            global_counts, split_counts = context_counts(lines, seqs, field, alphabet, order)
            contexts = sorted(global_counts); base = sum(c_bits(global_counts[c], alphabet) for c in contexts)
            candidates = []
            for c in contexts:
                split = sum(c_bits(counts, alphabet) for counts in split_counts[c].values())
                candidates.append((c_bits(global_counts[c], alphabet) - split, c, split))
            candidates.sort(key=lambda x: (-x[0], x[1])); n = len(candidates)
            best = None
            cumulative = 0.0
            for k in range(n + 1):
                if k: cumulative += candidates[k - 1][0]
                subset = universal_uint_bits(k) + (math.log2(math.comb(n, k)) if 0 < k < n else 0.0)
                key = 3.0 + math.log2(len(AXES)) + math.log2(3) + rare_key + subset
                payload = base - cumulative; total = fixed + side + key + payload
                candidate = (total, k, key, payload)
                if best is None or candidate < best: best = candidate
            total, k, key, payload = best; selected = candidates[:k]
            decoder = {
                "schema": "GDT001_SPARSE_METADATA_SOURCE_DECODER_V1", "axis": axis_name,
                "field": field, "order": order, "alphabet": "".join(active) + " ",
                "rare_symbols": source["null_symbols"], "global_context_count": n,
                "selected_contexts": [{"context": list(ctx), "gross_split_gain_bits": gain,
                                       "metadata_values": sorted(split_counts[ctx])} for gain, ctx, _ in selected],
                "reconstruction": "unlisted contexts use one global KT table; listed contexts use the frozen metadata-specific KT table; ordered rare-event side channel restores rare signs",
            }
            digest = hashlib.sha256(canonical(decoder)).hexdigest()
            row = {"axis": axis_name, "order": order, "selected_contexts": k, "available_contexts": n,
                   "total_bits": total, "bits_per_symbol": total / symbols,
                   "gap_vs_full_currier_bits": total - old["total_bits"],
                   "gap_vs_source_winner_bits": total - source["total_bits"], "key_bits": key,
                   "side_channel_bits": side, "payload_bits": payload, "fixed_bits": fixed,
                   "decoder_hash": digest, "cpu_exact": True}
            rows.append(row); codebooks.append(decoder | {"decoder_hash": digest})
    winner = min(rows, key=lambda x: x["total_bits"])
    decision = ("CONTINUE" if winner["gap_vs_full_currier_bits"] < 0 else "STOP") + "_SPARSE_METADATA_SOURCE"
    result = {"schema": "GDT001_SPARSE_METADATA_SOURCE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": winner, "rows": rows,
              "claim_ceiling": "Exploratory sparse source-process heterogeneity only; no sign value, language, cipher, meaning, or plaintext is established."}
    (ROOT / "gdt001_sparse_metadata_source_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_sparse_metadata_source_codebooks.json").write_bytes(canonical({"schema": "GDT001_SPARSE_METADATA_SOURCE_CODEBOOKS_V1", "codebooks": codebooks}))
    with (ROOT / "gdt001_sparse_metadata_source_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": winner}))


if __name__ == "__main__":
    main()
