#!/usr/bin/env python3
"""Reversible source model whose decoded line entry selects the body process."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


SCHEMES = ("FIRST_CHAR", "FIRST_TWO", "FIRST_GROUP_LENGTH", "FIRST_CHAR_GROUP_LENGTH")


def state_for(seq, words, scheme):
    first = seq[0] if seq else -1; length = min(len(words[0]), 12) if words else 0
    if scheme == "FIRST_CHAR": return (first,)
    if scheme == "FIRST_TWO": return tuple(seq[:2])
    if scheme == "FIRST_GROUP_LENGTH": return (length,)
    return (first, length)


def kt_events(events, alphabet, order):
    tables = defaultdict(Counter); bos = alphabet
    for state, seq in events:
        history = [bos] * order
        for token in seq:
            tables[(state, tuple(history))][token] += 1
            if order: history = history[1:] + [token]
    return sum(categorical_bits([counts.get(i, 0) for i in range(alphabet)]) for counts in tables.values()), len(tables)


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words)
    source = json.loads((ROOT / "gdt001_source_selected_null_results.json").read_text())["selected_source_null"]
    leader = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())["best"]
    nulls = frozenset(source["null_symbols"]); seqs, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1
    rare_key = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
    rows = []; decoders = []
    for scheme in SCHEMES:
        for order in range(4):
            headers = []; bodies = []; state_counts = Counter()
            for path, seq in zip(paths, seqs):
                width = 1 if scheme in ("FIRST_CHAR", "FIRST_GROUP_LENGTH", "FIRST_CHAR_GROUP_LENGTH") else min(2, len(seq))
                header = seq[:width]; state = state_for(seq, path.words, scheme); state_counts[state] += 1
                headers.append((("HEADER",), header)); bodies.append((state, seq[width:]))
            header_bits, header_contexts = kt_events(headers, alphabet, order)
            body_bits, body_contexts = kt_events(bodies, alphabet, order)
            # For length-based state, the exact first-group length must be
            # transmitted before the body; first-char/two states are already
            # present in the decoded header.
            length_side = 0.0
            if "LENGTH" in scheme:
                lengths = Counter(min(len(p.words[0]), 12) if p.words else 0 for p in paths)
                length_side = categorical_bits([lengths[i] for i in range(13)])
            key = 3.0 + math.log2(len(SCHEMES)) + rare_key + universal_uint_bits(order)
            payload = header_bits + body_bits + length_side; total = fixed + side + key + payload
            decoder = {"schema": "GDT001_ENTRY_CONDITIONED_SOURCE_DECODER_V1", "scheme": scheme, "order": order,
                       "state_count": len(state_counts), "state_counts": {"|".join(map(str, k)): v for k, v in sorted(state_counts.items())},
                       "rare_symbols": source["null_symbols"],
                       "reconstruction": "decode the line header globally; derive or decode the frozen entry state; decode the remainder from its state-specific integrated KT process; restore rare signs"}
            digest = hashlib.sha256(canonical(decoder)).hexdigest()
            rows.append({"scheme": scheme, "order": order, "states": len(state_counts), "header_contexts": header_contexts,
                         "body_contexts": body_contexts, "total_bits": total, "bits_per_symbol": total / symbols,
                         "gap_vs_context_axis_bits": total - leader["total_bits"], "gap_vs_source_winner_bits": total - source["total_bits"],
                         "key_bits": key, "side_channel_bits": side + length_side, "payload_bits": header_bits + body_bits,
                         "fixed_bits": fixed, "decoder_hash": digest, "cpu_exact": True})
            decoders.append(decoder | {"decoder_hash": digest})
    best = min(rows, key=lambda r: r["total_bits"])
    decision = ("CONTINUE" if best["gap_vs_context_axis_bits"] < 0 else "STOP") + "_ENTRY_CONDITIONED_SOURCE"
    result = {"schema": "GDT001_ENTRY_CONDITIONED_SOURCE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": best, "rows": rows,
              "claim_ceiling": "Exploratory line-entry-conditioned source process only; entry states have no word, syntax, language, cipher, or semantic interpretation."}
    (ROOT / "gdt001_entry_conditioned_source_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_entry_conditioned_source_decoders.json").write_bytes(canonical({"schema": "GDT001_ENTRY_CONDITIONED_SOURCE_DECODERS_V1", "decoders": decoders}))
    with (ROOT / "gdt001_entry_conditioned_source_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__":
    main()
