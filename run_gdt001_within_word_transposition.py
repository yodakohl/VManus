#!/usr/bin/env python3
"""Explicit reversible within-word transpositions for language/cipher search."""

import csv, hashlib, json, math

import numpy as np

from gdt001_core import ROOT, LETTERS, canonical, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_language_models import PACK_NAMES, train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


SCHEMES = ("REVERSE", "ODD_EVEN", "EVEN_ODD", "OUTSIDE_IN", "INSIDE_OUT")


def reorder(word, scheme):
    n = len(word)
    if scheme == "REVERSE": return word[::-1]
    if scheme == "ODD_EVEN": return word[::2] + word[1::2]
    if scheme == "EVEN_ODD": return word[1::2] + word[::2]
    if scheme == "OUTSIDE_IN":
        order = []; left = 0; right = n - 1
        while left <= right:
            order.append(left); left += 1
            if left <= right: order.append(right); right -= 1
        return "".join(word[i] for i in order)
    center = (n - 1) // 2; order = []; delta = 0
    while len(order) < n:
        for index in ((center - delta) if delta else center, center + delta + (0 if n % 2 == 0 else 1)):
            if 0 <= index < n and index not in order: order.append(index)
        delta += 1
    return "".join(word[i] for i in order)


def encoded(paths, scheme):
    seqs = []; counts = np.zeros(25); space = 25
    for path in paths:
        seq = []
        for wi, raw in enumerate(path.words):
            if wi: seq.append(space)
            for char in reorder(raw, scheme):
                token = LETTERS.index(char); seq.append(token); counts[token] += 1
        seqs.append(seq)
    return seqs, counts, np.zeros(25, dtype=np.int64), list(LETTERS), space


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words)
    leader = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())["best"]
    rows = []; mappings = []; screen = []
    for scheme in SCHEMES:
        args = encoded(paths, scheme); null_payload = kt_ngram_bits(args[0], 26, 2)
        null_key = 3.0 + math.log2(len(SCHEMES)) + universal_uint_bits(2); null_total = fixed + null_key + null_payload
        null_decoder = hashlib.sha256(canonical({"scheme": scheme, "order": 2})).hexdigest()
        rows.append({"model": "MATCHED_TRANSPOSITION_NULL", "scheme": scheme, "language": "_", "seed": 0,
                     "total_bits": null_total, "bits_per_symbol": null_total / symbols,
                     "gap_vs_matched_null_bits": 0.0, "gap_vs_context_axis_bits": null_total - leader["total_bits"],
                     "key_bits": null_key, "payload_bits": null_payload, "fixed_bits": fixed,
                     "decoder_hash": null_decoder, "cpu_exact": True})
        for language in PACK_NAMES:
            bits, mapping, digest = search_encoded(*args, train_pack(language, 2), 29101, population=4096, generations=15)
            key = 3.0 + math.log2(len(SCHEMES)) + math.log2(len(PACK_NAMES)) + universal_uint_bits(2) + 25 * math.log2(27)
            total = fixed + key + bits
            item = {"model": "TRANSPOSITION_LANGUAGE", "scheme": scheme, "language": language, "seed": 29101,
                    "total_bits": total, "bits_per_symbol": total / symbols,
                    "gap_vs_matched_null_bits": total - null_total, "gap_vs_context_axis_bits": total - leader["total_bits"],
                    "key_bits": key, "payload_bits": bits, "fixed_bits": fixed, "decoder_hash": digest, "cpu_exact": True}
            rows.append(item); screen.append(item); mappings.append(item | {"mapping": mapping})
    winner = min(screen, key=lambda r: r["total_bits"]); args = encoded(paths, winner["scheme"]); lm = train_pack(winner["language"], 2)
    null_total = next(r["total_bits"] for r in rows if r["model"] == "MATCHED_TRANSPOSITION_NULL" and r["scheme"] == winner["scheme"])
    for seed in (29102, 29103):
        bits, mapping, digest = search_encoded(*args, lm, seed, population=4096, generations=15)
        key = 3.0 + math.log2(len(SCHEMES)) + math.log2(len(PACK_NAMES)) + universal_uint_bits(2) + 25 * math.log2(27); total = fixed + key + bits
        item = {"model": "TRANSPOSITION_LANGUAGE", "scheme": winner["scheme"], "language": winner["language"], "seed": seed,
                "total_bits": total, "bits_per_symbol": total / symbols, "gap_vs_matched_null_bits": total - null_total,
                "gap_vs_context_axis_bits": total - leader["total_bits"], "key_bits": key, "payload_bits": bits,
                "fixed_bits": fixed, "decoder_hash": digest, "cpu_exact": True}
        rows.append(item); mappings.append(item | {"mapping": mapping})
    best = min((r for r in rows if r["model"] == "TRANSPOSITION_LANGUAGE"), key=lambda r: r["total_bits"])
    same = [r for r in rows if r["model"] == "TRANSPOSITION_LANGUAGE" and r["scheme"] == winner["scheme"] and r["language"] == winner["language"]]
    stable = len({r["decoder_hash"] for r in same}) == 1
    decision = ("CONTINUE" if best["gap_vs_matched_null_bits"] < 0 else "STOP") + "_WITHIN_WORD_TRANSPOSITION_" + ("STABLE" if stable else "UNSTABLE")
    result = {"schema": "GDT001_WITHIN_WORD_TRANSPOSITION_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": best, "rows": rows,
              "claim_ceiling": "Exploratory reversible reading-order and language-key search only; no direction, language, plaintext, or translation is established."}
    (ROOT / "gdt001_within_word_transposition_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_within_word_transposition_mappings.json").write_bytes(canonical({"schema": "GDT001_WITHIN_WORD_TRANSPOSITION_MAPPINGS_V1", "mappings": mappings}))
    with (ROOT / "gdt001_within_word_transposition_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__":
    main()
