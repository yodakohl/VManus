#!/usr/bin/env python3
"""Exact KT source models conditioned on known manuscript metadata."""

import csv, hashlib, json, math
from collections import defaultdict

from gdt001_core import ROOT, SOURCE_ALPHABET, canonical, fixed_costs, kt_ngram_bits, kt_ngram_components, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


FIELDS = (
    ("GLOBAL", ()), ("CURRIER", ("currier",)), ("SECTION", ("section",)),
    ("HAND", ("hand",)), ("KIND", ("kind",)), ("CODE", ("code",)),
    ("GRAMMAR_SCOPE", ("grammar_scope",)),
    ("CURRIER_SECTION", ("currier", "section")),
    ("SECTION_HAND", ("section", "hand")),
    ("KIND_GRAMMAR_SCOPE", ("kind", "grammar_scope")),
    ("PAGE", ("page",)),
)


def buckets(lines, seqs, fields):
    out = defaultdict(list)
    for line, seq in zip(lines, seqs):
        key = tuple(getattr(line, f) or "_" for f in fields) if fields else ("_",)
        out[key].append(seq)
    return out


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines)
    fixed = sum(fixed_costs(paths).values()); symbols = sum(len(w) for p in paths for w in p.words)
    source = json.loads((ROOT / "gdt001_source_selected_null_results.json").read_text())["selected_source_null"]
    raw_seqs = [p.source_ids for p in paths]
    nulls = frozenset(source["null_symbols"])
    null_seqs, _, _, active, _, null_channel = encoded(paths, nulls)
    variants = (("RAW", raw_seqs, len(SOURCE_ALPHABET), 0.0),
                ("RARE_CHANNEL", null_seqs, len(active) + 1, null_channel))
    rows = []; decoders = []
    for variant, seqs, alphabet, side_bits in variants:
        rare_key = (universal_uint_bits(len(nulls)) + math.log2(math.comb(len(SOURCE_ALPHABET) - 1, len(nulls)))) if variant == "RARE_CHANNEL" else 0.0
        for field_name, fields in FIELDS:
            grouped = buckets(lines, seqs, fields)
            for order in range(6):
                payload = sum(kt_ngram_bits(grouped[key], alphabet, order) for key in sorted(grouped))
                key = 3.0 + math.log2(len(FIELDS)) + 1.0 + universal_uint_bits(order) + rare_key
                total = fixed + side_bits + key + payload
                decoder = {
                    "schema": "GDT001_METADATA_SOURCE_DECODER_V1", "variant": variant,
                    "conditioning": field_name, "fields": list(fields), "order": order,
                    "contexts": [list(key_) for key_ in sorted(grouped)],
                    "rare_symbols": source["null_symbols"] if variant == "RARE_CHANNEL" else "",
                    "reconstruction": "metadata selects an integrated KT character process; optional ordered rare-event channel restores deleted source signs",
                }
                digest = hashlib.sha256(canonical(decoder)).hexdigest()
                rows.append({
                    "variant": variant, "conditioning": field_name, "order": order,
                    "metadata_contexts": len(grouped), "total_bits": total,
                    "bits_per_symbol": total / symbols,
                    "gap_vs_source_winner_bits": total - source["total_bits"],
                    "key_bits": key, "side_channel_bits": side_bits,
                    "payload_bits": payload, "fixed_bits": fixed,
                    "decoder_hash": digest, "cpu_exact": True,
                })
                decoders.append(decoder | {"decoder_hash": digest})
    best = min(rows, key=lambda row: row["total_bits"])
    best_fields = dict(FIELDS)[best["conditioning"]]
    best_seqs = null_seqs if best["variant"] == "RARE_CHANNEL" else raw_seqs
    best_alphabet = len(active) + 1 if best["variant"] == "RARE_CHANNEL" else len(SOURCE_ALPHABET)
    tables = []
    for metadata, group_seqs in sorted(buckets(lines, best_seqs, best_fields).items()):
        bits, components = kt_ngram_components(group_seqs, best_alphabet, best["order"])
        tables.append({"metadata": list(metadata), "bits": bits, "contexts": components})
    codebook = {
        "schema": "GDT001_METADATA_SOURCE_CODEBOOK_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
        "conditioning": best["conditioning"], "fields": list(best_fields), "order": best["order"],
        "source_alphabet": SOURCE_ALPHABET, "active_alphabet": "".join(active) + " ",
        "rare_symbols": source["null_symbols"], "rare_channel_bits": null_channel,
        "tables": tables, "decoder_hash": best["decoder_hash"],
        "reconstruction": "Select the table by frozen line metadata; decode each line-reset KT context, then decode the ordered binary rare-event stream and rare identity stream to restore every deleted sign.",
    }
    decision = ("CONTINUE" if best["gap_vs_source_winner_bits"] < 0 else "STOP") + "_METADATA_CONDITIONED_SOURCE"
    result = {
        "schema": "GDT001_METADATA_CONDITIONED_SOURCE_V1",
        "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "decision": decision,
        "best": best, "rows": rows,
        "claim_ceiling": "Exploratory reversible source compression conditioned on catalogue metadata; no metadata value, source sign, word, language, meaning, or plaintext interpretation is established.",
    }
    (ROOT / "gdt001_metadata_conditioned_source_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_metadata_conditioned_source_decoders.json").write_bytes(canonical({"schema": "GDT001_METADATA_SOURCE_DECODERS_V1", "decoders": decoders}))
    (ROOT / "gdt001_metadata_conditioned_source_codebook.json").write_bytes(canonical(codebook))
    with (ROOT / "gdt001_metadata_conditioned_source_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__":
    main()
