#!/usr/bin/env python3
"""All-language screen on the explicit shared prefix/core/suffix scaffold."""

import csv, hashlib, json, math

from gdt001_core import ROOT, canonical, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_language_models import PACK_NAMES, TARGET_LETTERS, evolve_mapping, explicit_mapping, homophone_reverse_bits, path_language_bits, source_unigrams, train_pack
from gdt001_scaffold_payload import common_selected_paths, scaffold_and_payload, scaffold_rule_bits


def fit(paths, payloads, scaffold_bits, fixed, language, seed):
    lm = train_pack(language, 2)
    mapping, _, search = evolve_mapping(lm, payloads, seed=seed, injective=False,
                                         population_size=8192, generations=18, cuda=True)
    language_bits = sum(path_language_bits(lm, mapping, path) for path in payloads)
    reverse_bits = homophone_reverse_bits(mapping, source_unigrams(payloads))
    key = 3.0 + math.log2(len(PACK_NAMES)) + scaffold_rule_bits() + len(__import__("gdt001_core").LETTERS) * math.log2(len(TARGET_LETTERS)) + universal_uint_bits(2)
    total = key + scaffold_bits + language_bits + reverse_bits + fixed
    mapped = explicit_mapping(mapping, True, payloads); digest = hashlib.sha256(canonical(mapped)).hexdigest()
    return {"language": language, "seed": seed, "total_bits": total,
            "key_bits": key, "scaffold_bits": scaffold_bits,
            "language_bits": language_bits, "reverse_bits": reverse_bits, "fixed_bits": fixed,
            "decoder_hash": digest, "mapping": mapped, "cpu_exact": abs(search["cpu_reconstruction_score"] - (language_bits + reverse_bits)) < 1e-6}


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); scaffold_bits, payloads, scaffold = scaffold_and_payload(paths)
    fixed = sum(fixed_costs(paths).values()); symbols = sum(len(w) for p in paths for w in p.words)
    null_payload = kt_ngram_bits([p.source_ids for p in payloads], 26, 2)
    null_key = 3.0 + scaffold_rule_bits() + universal_uint_bits(2)
    null_total = null_key + scaffold_bits + null_payload + fixed
    rows = []; mappings = []
    for language in PACK_NAMES:
        item = fit(paths, payloads, scaffold_bits, fixed, language, 30101); item["bits_per_symbol"] = item["total_bits"] / symbols
        item["gap_vs_matched_null_bits"] = item["total_bits"] - null_total; mappings.append({"language": language, "seed": 30101, "decoder_hash": item["decoder_hash"], "mapping": item.pop("mapping")}); rows.append(item)
    winner = min(rows, key=lambda r: r["total_bits"])
    for seed in (30102, 30103):
        item = fit(paths, payloads, scaffold_bits, fixed, winner["language"], seed); item["bits_per_symbol"] = item["total_bits"] / symbols
        item["gap_vs_matched_null_bits"] = item["total_bits"] - null_total; mappings.append({"language": item["language"], "seed": seed, "decoder_hash": item["decoder_hash"], "mapping": item.pop("mapping")}); rows.append(item)
    best = min(rows, key=lambda r: r["total_bits"]); same = [r for r in rows if r["language"] == winner["language"]]
    stable = len({r["decoder_hash"] for r in same}) == 1
    decision = ("CONTINUE" if best["gap_vs_matched_null_bits"] < 0 else "STOP") + "_SCAFFOLD_LANGUAGES_" + ("STABLE" if stable else "UNSTABLE")
    result = {"schema": "GDT001_SCAFFOLD_LANGUAGES_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "matched_null": {"total_bits": null_total, "bits_per_symbol": null_total / symbols,
              "key_bits": null_key, "scaffold_bits": scaffold_bits, "payload_bits": null_payload, "fixed_bits": fixed},
              "best": best, "rows": rows,
              "claim_ceiling": "Exploratory language decoding of anonymous scaffold cores only; no prefix, suffix, core, language, meaning, plaintext, or translation is established."}
    (ROOT / "gdt001_scaffold_language_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_scaffold_language_mappings.json").write_bytes(canonical({"schema": "GDT001_SCAFFOLD_LANGUAGE_MAPPINGS_V1", "mappings": mappings}))
    with (ROOT / "gdt001_scaffold_language_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best, "matched_null_bps": null_total / symbols}))


if __name__ == "__main__":
    main()
