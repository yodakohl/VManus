#!/usr/bin/env python3
"""Focused explicit decoder screen with the pinned scholastic Latin pack."""

import csv, hashlib, json, math
from collections import Counter

import numpy as np

from gdt001_core import ROOT, LETTERS, TARGET_ALPHABET, canonical, fixed_costs, load_lattice, universal_uint_bits
from gdt001_language_models import NgramLM, TARGET_LETTERS, evolve_mapping, explicit_mapping, homophone_reverse_bits, path_language_bits, source_unigrams
from gdt001_scaffold_payload import common_selected_paths, scaffold_and_payload, scaffold_rule_bits
from run_gdt001_contextual_language import search_encoded
from run_gdt001_group_character_code import encoded as group_encoded


def lm(order=2, alpha=.5):
    size = len(TARGET_ALPHABET); shape = (size + 1,) * order + (size,); counts = np.zeros(shape); letters = 0
    for raw in (ROOT / ".gdt001/language_packs/latin_scholastic.txt").read_text().splitlines():
        ids = [TARGET_ALPHABET.index(c) for c in raw]; letters += sum(i != 26 for i in ids); history = [27] * order
        for token in ids:
            counts[tuple(history) + (token,)] += 1
            if order: history = history[1:] + [token]
    return NgramLM("latin_scholastic", order, -np.log2((counts + alpha) / (counts.sum(axis=-1, keepdims=True) + alpha * size)), letters)


def direct(paths, language_model, seed):
    seqs = [list(p.source_ids) for p in paths]; counts = np.zeros(25)
    for p in paths:
        for c in p.source_line.replace(" ", ""): counts[LETTERS.index(c)] += 1
    bits, mapping, digest = search_encoded(seqs, counts, np.zeros(25, dtype=np.int64), list(LETTERS), 25,
                                            language_model, seed, population=8192, generations=18)
    return bits, mapping, digest, 25 * math.log2(27)


def group(paths, language_model, seed, k=128):
    seqs, counts, cats, vocab, space, common = group_encoded(paths, k)
    bits, mapping, digest = search_encoded(seqs, counts, cats, vocab, space, language_model, seed,
                                            population=8192, generations=18)
    return bits + common, mapping, digest, k * math.log2(27)


def scaffold(paths, language_model, seed):
    scaffold_bits, payloads, _ = scaffold_and_payload(paths)
    mapping, _, search = evolve_mapping(language_model, payloads, seed=seed, injective=False,
                                         population_size=8192, generations=18, cuda=True)
    language_bits = sum(path_language_bits(language_model, mapping, p) for p in payloads)
    reverse = homophone_reverse_bits(mapping, source_unigrams(payloads)); mapped = explicit_mapping(mapping, True, payloads)
    digest = hashlib.sha256(canonical(mapped)).hexdigest()
    assert abs(search["cpu_reconstruction_score"] - (language_bits + reverse)) < 1e-6
    return scaffold_bits + language_bits + reverse, mapped, digest, scaffold_rule_bits() + 25 * math.log2(26)


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words); language_model = lm(2)
    variable = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]
    group_results = json.loads((ROOT / "gdt001_group_character_code_results.json").read_text())
    group_null = next(r for r in group_results["rows"] if r["model"] == "MATCHED_GROUP_CODE_NULL" and r["k"] == 128)
    scaffold_null = json.loads((ROOT / "gdt001_scaffold_language_results.json").read_text())["matched_null"]
    matched = {"DIRECT": variable["total_bits"], "GROUP_K128": group_null["total_bits"], "SCAFFOLD_CORE": scaffold_null["total_bits"]}
    functions = {"DIRECT": direct, "GROUP_K128": group, "SCAFFOLD_CORE": scaffold}; rows = []; mappings = []
    for model, function in functions.items():
        for seed in (32101, 32102, 32103):
            payload, mapping, digest, mapping_key = function(paths, language_model, seed)
            key = 3.0 + math.log2(3) + math.log2(7) + universal_uint_bits(2) + mapping_key
            total = fixed + key + payload
            row = {"model": model, "language": "latin_scholastic", "seed": seed, "total_bits": total,
                   "bits_per_symbol": total / symbols, "gap_vs_matched_null_bits": total - matched[model],
                   "key_bits": key, "payload_bits": payload, "fixed_bits": fixed,
                   "decoder_hash": digest, "cpu_exact": True}
            rows.append(row); mappings.append(row | {"mapping": mapping})
    best = min(rows, key=lambda r: r["total_bits"]); same = [r for r in rows if r["model"] == best["model"]]
    stable = len({r["decoder_hash"] for r in same}) == 1
    decision = ("CONTINUE" if best["gap_vs_matched_null_bits"] < 0 else "STOP") + "_LATIN_SCHOLASTIC_" + ("STABLE" if stable else "UNSTABLE")
    result = {"schema": "GDT001_LATIN_SCHOLASTIC_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "pack_sha256": json.loads((ROOT / "gdt001_latin_scholastic_pack.json").read_text())["prepared_sha256"],
              "best": best, "rows": rows,
              "claim_ceiling": "Exploratory pinned scholastic Latin decoder screen only; no Latin reading, plaintext, meaning, or translation is established."}
    (ROOT / "gdt001_latin_scholastic_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_latin_scholastic_mappings.json").write_bytes(canonical({"schema": "GDT001_LATIN_SCHOLASTIC_MAPPINGS_V1", "mappings": mappings}))
    with (ROOT / "gdt001_latin_scholastic_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__":
    main()
