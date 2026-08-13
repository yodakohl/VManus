#!/usr/bin/env python3
"""Zero-permutation rank-frequency whole-group nomenclator."""

import csv, hashlib, json, math
from collections import Counter

from gdt001_controls import CONTROL_NAMES, transform
from gdt001_core import ROOT, canonical, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_language_models import PACK_NAMES
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_word_nomenclator import split


LANGUAGES = PACK_NAMES + ("latin_scholastic",)
KS = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)


def corpus(language, k, alpha=.5):
    frequency = Counter(word for line in (ROOT / ".gdt001/language_packs" / f"{language}.txt").read_text().splitlines() for word in line.split())
    vocab = [word for word, _ in sorted(frequency.items(), key=lambda x: (-x[1], x[0]))[:k]]
    denominator = sum(frequency[word] for word in vocab) + alpha * len(vocab)
    costs = [-math.log2((frequency[word] + alpha) / denominator) for word in vocab]
    return vocab, costs


def fit(paths, languages=LANGUAGES):
    fixed = sum(fixed_costs(paths).values()); symbols = sum(len(word) for path in paths for word in path.words)
    rows = []; decoders = []
    for k in KS:
        source, runs, common = split(paths, k); counts = Counter(token for run in runs for token in run)
        null_payload = kt_ngram_bits(runs, k, 0); null_key = 3.0 + math.log2(len(KS)) + universal_uint_bits(0) + common
        null_total = fixed + null_key + null_payload
        rows.append({"model": "MATCHED_RANK_NULL", "k": k, "language": "_", "total_bits": null_total,
                     "bits_per_symbol": null_total / symbols, "gap_vs_matched_null_bits": 0.0,
                     "key_bits": null_key, "payload_bits": null_payload, "fixed_bits": fixed,
                     "decoder_hash": hashlib.sha256(canonical({"source": source, "order": 0})).hexdigest(), "cpu_exact": True})
        for language in languages:
            target, costs = corpus(language, k); effective = min(len(target), k)
            if effective < k: continue
            payload = sum(counts[i] * costs[i] for i in range(k))
            key = 3.0 + math.log2(len(KS)) + math.log2(len(LANGUAGES)) + universal_uint_bits(0) + common
            total = fixed + key + payload
            mapping = [{"source_group": source[i], "target_word": target[i], "source_occurrences": counts[i],
                        "rule": f"FREQUENCY_RANK_{i + 1}"} for i in range(k)]
            digest = hashlib.sha256(canonical(mapping)).hexdigest()
            rows.append({"model": "RANK_NOMENCLATOR", "k": k, "language": language, "total_bits": total,
                         "bits_per_symbol": total / symbols, "gap_vs_matched_null_bits": total - null_total,
                         "key_bits": key, "payload_bits": payload, "fixed_bits": fixed,
                         "decoder_hash": digest, "cpu_exact": True})
            decoders.append({"k": k, "language": language, "decoder_hash": digest, "mapping": mapping})
    return rows, decoders


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); rows, decoders = fit(paths)
    best = min((r for r in rows if r["model"] == "RANK_NOMENCLATOR"), key=lambda r: r["total_bits"])
    control_rows = []
    for name in CONTROL_NAMES:
        changed = transform(lines, paths, name); current, _ = fit(changed, (best["language"],))
        candidate = next(r for r in current if r["model"] == "RANK_NOMENCLATOR" and r["k"] == best["k"])
        control_rows.append({"control": name, "gap_vs_matched_null_bits": candidate["gap_vs_matched_null_bits"],
                             "bits_per_symbol": candidate["bits_per_symbol"]})
    specific = best["gap_vs_matched_null_bits"] < min(r["gap_vs_matched_null_bits"] for r in control_rows)
    decision = ("CONTINUE" if best["gap_vs_matched_null_bits"] < 0 and specific else "STOP") + "_RANK_NOMENCLATOR_" + ("REAL_SPECIFIC" if specific else "NOT_SPECIFIC")
    result = {"schema": "GDT001_RANK_NOMENCLATOR_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": best, "controls": control_rows, "rows": rows,
              "claim_ceiling": "Exploratory frequency-rank codebook only; plausible common target words can arise from Zipf structure and are not readings, meanings, plaintext, or translation."}
    (ROOT / "gdt001_rank_nomenclator_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_rank_nomenclator_decoders.json").write_bytes(canonical({"schema": "GDT001_RANK_NOMENCLATOR_DECODERS_V1", "decoders": decoders}))
    with (ROOT / "gdt001_rank_nomenclator_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best, "controls": control_rows}))


if __name__ == "__main__":
    main()
