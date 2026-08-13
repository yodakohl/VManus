#!/usr/bin/env python3
"""Exact page-local word cache with a reversible literal fallback."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths


WINDOWS = (4, 8, 16, 32, 64, 128, 256)
MIN_LENGTHS = (1, 2, 3, 4, 5, 6, 8)
ORDERS = (0, 1, 2, 3)


def events(lines, paths, window, minimum):
    caches = defaultdict(list); modes = Counter(); literals = []; lengths = Counter(); index_bits = 0.0
    copies_by_distance = Counter(); line_counts = Counter(); copy_events = 0
    for line, path in zip(lines, paths):
        line_counts[len(path.words)] += 1; cache = caches[line.page]
        for word in path.words:
            try: index = cache.index(word)
            except ValueError: index = -1
            if len(word) >= minimum and 0 <= index < min(window, len(cache)):
                modes["COPY"] += 1; copy_events += 1; available = min(window, len(cache)); index_bits += math.log2(available)
                copies_by_distance[index + 1] += 1
            else:
                modes["LITERAL"] += 1; lengths[len(word)] += 1
                literals.append(tuple(LETTERS.index(c) for c in word))
            if word in cache: cache.remove(word)
            cache.insert(0, word)
            if len(cache) > window: del cache[window:]
    max_line = max(line_counts); max_length = max(lengths, default=0)
    structure = universal_uint_bits(max_line) + categorical_bits([line_counts[i] for i in range(max_line + 1)])
    structure += categorical_bits([modes["LITERAL"], modes["COPY"]])
    structure += universal_uint_bits(max_length) + categorical_bits([lengths[i] for i in range(max_length + 1)])
    return literals, structure + index_bits, {"modes": dict(modes), "copy_events": copy_events,
            "copy_distance_counts": dict(sorted(copies_by_distance.items())), "line_word_counts": dict(sorted(line_counts.items())),
            "literal_length_counts": dict(sorted(lengths.items())), "copy_index_bits": index_bits}


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words)
    leader = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())["best"]
    source = json.loads((ROOT / "gdt001_source_selected_null_results.json").read_text())["selected_source_null"]
    rows = []; decoders = []
    for window in WINDOWS:
        for minimum in MIN_LENGTHS:
            literals, structure, stats = events(lines, paths, window, minimum)
            for order in ORDERS:
                literal_bits = kt_ngram_bits(literals, len(LETTERS), order)
                key = 3.0 + math.log2(len(WINDOWS)) + math.log2(len(MIN_LENGTHS)) + math.log2(len(ORDERS))
                total = fixed + key + structure + literal_bits
                decoder = {"schema": "GDT001_EXACT_COPY_CACHE_DECODER_V1", "history_scope": "PAGE",
                           "window": window, "minimum_copy_length": minimum, "literal_order": order,
                           "cache_rule": "most-recently-used distinct complete source forms",
                           "stats": stats,
                           "reconstruction": "decode physical-line word count; COPY selects a cache index, LITERAL decodes a length and KT character sequence; update the deterministic MRU cache"}
                digest = hashlib.sha256(canonical(decoder)).hexdigest()
                rows.append({"window": window, "minimum_copy_length": minimum, "literal_order": order,
                             "copy_events": stats["copy_events"], "total_bits": total, "bits_per_symbol": total / symbols,
                             "gap_vs_context_axis_bits": total - leader["total_bits"],
                             "gap_vs_source_winner_bits": total - source["total_bits"], "key_bits": key,
                             "structure_and_index_bits": structure, "literal_bits": literal_bits, "fixed_bits": fixed,
                             "decoder_hash": digest, "cpu_exact": True})
                decoders.append(decoder | {"decoder_hash": digest})
    best = min(rows, key=lambda r: r["total_bits"])
    decision = ("CONTINUE" if best["gap_vs_context_axis_bits"] < 0 else "STOP") + "_EXACT_COPY_CACHE"
    result = {"schema": "GDT001_EXACT_COPY_CACHE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": best, "rows": rows,
              "claim_ceiling": "Exploratory formal recency cache only; a copy code does not establish scribal chronology, language, meaning, or plaintext."}
    (ROOT / "gdt001_exact_copy_cache_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_exact_copy_cache_decoders.json").write_bytes(canonical({"schema": "GDT001_EXACT_COPY_CACHE_DECODERS_V1", "decoders": decoders}))
    with (ROOT / "gdt001_exact_copy_cache_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__":
    main()
