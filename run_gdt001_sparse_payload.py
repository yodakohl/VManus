#!/usr/bin/env python3
"""Fast matched-null test for language confined to structural payload slots."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from dataclasses import replace

from gdt001_core import ROOT, SOURCE_ALPHABET, canonical, fixed_costs, kt_ngram_bits, score_record, universal_uint_bits
from gdt001_language_models import TARGET_LETTERS, evolve_mapping, explicit_mapping, homophone_reverse_bits, path_language_bits, source_unigrams, train_pack
from gdt001_record_models import decompose
from gdt001_scaffold_payload import common_selected_paths, scaffold_and_payload, scaffold_rule_bits


SELECTORS = ("BODY", "LATE_HALF", "LONG_CORE", "BODY_LONG_CORE", "CHE_PREFIX")


def occurrence_paths(paths, selector):
    selected = []; other = []
    for path in paths:
        n = len(path.words)
        for position, word in enumerate(path.words):
            _, core, _ = decompose(word)
            choose = {
                "BODY": position > 0,
                "LATE_HALF": position >= (n + 1) // 2,
                "LONG_CORE": len(core) >= 4,
                "BODY_LONG_CORE": position > 0 and len(core) >= 4,
                "CHE_PREFIX": word.startswith("che") and len(word) > 3,
            }[selector]
            item = replace(path, words=(core,), source_line=core,
                           source_ids=tuple(SOURCE_ALPHABET.index(c) for c in core),
                           fixed_bits=0.0, choice_bits=0.0, raw_residual_bits=0.0,
                           separator_bits=0.0, path_id=f"{path.path_id}|{position}")
            (selected if choose else other).append(item)
    return selected, other


def main():
    _, lines = __import__("gdt001_core").load_lattice(); paths = common_selected_paths(lines)
    scaffold_bits, _, _ = scaffold_and_payload(paths); fixed = sum(fixed_costs(paths).values())
    lm = train_pack("middle_high_german", 2); rows = []; mappings = []
    selector_cost = math.log2(len(SELECTORS))
    cache_path = ROOT / ".gdt001/sparse_payload_cache.json"
    cached = json.loads(cache_path.read_text())["rows"] if cache_path.exists() else []
    cached_by_key = {(row["selector"], row["candidate"], row["seed"]): row for row in cached}
    for selector in SELECTORS:
        chosen, other = occurrence_paths(paths, selector)
        other_bits = kt_ngram_bits([p.source_ids for p in other], 26, 2)
        chosen_null_bits = kt_ngram_bits([p.source_ids for p in chosen], 26, 2)
        common_key = scaffold_rule_bits() + selector_cost + 2 * universal_uint_bits(2)
        null_total = 3 + common_key + scaffold_bits + fixed + other_bits + chosen_null_bits
        rows.append({"selector": selector, "candidate": "MATCHED_SPLIT_NULL", "seed": 0,
                     "selected_occurrences": len(chosen), "other_occurrences": len(other),
                     "total_bits": null_total, "bits_per_symbol": null_total / sum(len(p.source_line.replace(' ','')) for p in paths),
                     "selected_channel_bits": chosen_null_bits, "other_channel_bits": other_bits,
                     "decoder_hash": "MATCHED_NULL", "cpu_exact": True})
        for seed in (2301, 2302, 2303):
            key = (selector, "SPARSE_MHG_LANGUAGE", seed)
            if key in cached_by_key:
                rows.append(cached_by_key[key]); continue
            mapping, _, search = evolve_mapping(lm, chosen, seed=seed, injective=False,
                                                 population_size=32768, generations=30, cuda=True)
            language_bits = sum(path_language_bits(lm, mapping, p) for p in chosen)
            reverse = homophone_reverse_bits(mapping, source_unigrams(chosen))
            language_key = scaffold_rule_bits() + selector_cost + universal_uint_bits(2) + math.log2(6) + 25 * math.log2(26)
            total = 3 + language_key + scaffold_bits + fixed + other_bits + language_bits + reverse
            decoder = explicit_mapping(mapping, True, chosen)
            digest = __import__("hashlib").sha256(canonical(decoder)).hexdigest()
            rows.append({"selector": selector, "candidate": "SPARSE_MHG_LANGUAGE", "seed": seed,
                         "selected_occurrences": len(chosen), "other_occurrences": len(other),
                         "total_bits": total, "bits_per_symbol": total / sum(len(p.source_line.replace(' ','')) for p in paths),
                         "selected_channel_bits": language_bits + reverse, "other_channel_bits": other_bits,
                         "decoder_hash": digest, "cpu_exact": abs(search["cpu_reconstruction_score"] - (language_bits + reverse)) < 1e-6})
            mappings.append({"selector": selector, "seed": seed, "decoder_hash": digest, "mapping": decoder})
        cache_path.parent.mkdir(exist_ok=True)
        cache_path.write_bytes(canonical({"schema":"GDT001_SPARSE_PAYLOAD_CACHE_V1","rows":[row for row in rows if row["candidate"]=="SPARSE_MHG_LANGUAGE"]}))
    for selector in SELECTORS:
        null = next(r for r in rows if r["selector"] == selector and r["candidate"] == "MATCHED_SPLIT_NULL")
        for row in rows:
            if row["selector"] == selector and row["candidate"] == "SPARSE_MHG_LANGUAGE": row["gain_vs_matched_null_bits"] = null["total_bits"] - row["total_bits"]
        null["gain_vs_matched_null_bits"] = 0.0
    best_language = min((r for r in rows if r["candidate"] == "SPARSE_MHG_LANGUAGE"), key=lambda r:r["total_bits"])
    matched_null = next(r for r in rows if r["selector"] == best_language["selector"] and r["candidate"] == "MATCHED_SPLIT_NULL")
    stable = all(len({r["decoder_hash"] for r in rows if r["selector"] == selector and r["candidate"] == "SPARSE_MHG_LANGUAGE"}) == 1 for selector in SELECTORS)
    decision = "STOP_NO_SPARSE_LANGUAGE_GAIN" if best_language["total_bits"] >= matched_null["total_bits"] else "CONTINUE_SPARSE_LANGUAGE"
    if not stable: decision += "_KEYS_UNSTABLE"
    result = {"schema": "GDT001_SPARSE_PAYLOAD_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "selectors": list(SELECTORS), "selector_choice_bits": selector_cost,
              "common_path_source": "nonsemantic_ngram_o2", "common_fixed_bits": fixed,
              "best_language": best_language, "matched_null_for_best_selector": matched_null,
              "all_cpu_exact": all(r["cpu_exact"] for r in rows), "all_selector_keys_stable": stable,
              "rows": sorted(rows, key=lambda r:(r["selector"],r["candidate"],r["seed"])),
              "claim_ceiling": "Exploratory sparse payload test only; no language, plaintext, or nonsemantic-manuscript claim."}
    (ROOT / "gdt001_sparse_payload_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_sparse_payload_mappings.json").write_bytes(canonical({"schema":"GDT001_SPARSE_PAYLOAD_MAPPINGS_V1","mappings":mappings}))
    with (ROOT / "gdt001_sparse_payload_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        fields=list(result["rows"][0]); writer=csv.DictWriter(handle,fields,delimiter="\t",lineterminator="\n"); writer.writeheader(); writer.writerows(result["rows"])
    ledger_path = ROOT / "GDT001_YOLO_LEDGER.tsv"
    with ledger_path.open() as handle: ledger = list(csv.DictReader(handle, delimiter="\t"))
    ledger = [row for row in ledger if not row["run_id"].startswith("sparse_payload_")]
    for row in result["rows"]:
        run_id = f"sparse_payload_{row['selector'].lower()}_{'null' if row['candidate']=='MATCHED_SPLIT_NULL' else 'mhg'}_s{row['seed']:04d}"
        ledger.append({"run_id":run_id,"model_class":"NONSEMANTIC_GENERATOR" if row["candidate"]=="MATCHED_SPLIT_NULL" else "ABBR_LANG","language_or_system":f"SPARSE_{row['selector']}_{row['candidate']}","seed":str(row["seed"]),"config_hash":__import__("hashlib").sha256(canonical({"selector":row["selector"],"candidate":row["candidate"]})).hexdigest(),"total_bits":f"{row['total_bits']:.6f}","bits_per_symbol":f"{row['bits_per_symbol']:.9f}","key_bits":"0.000000","latent_bits":f"{row['selected_channel_bits']:.6f}","reconstruction_bits":f"{row['other_channel_bits'] + fixed:.6f}","exception_bits":"0.000000","convergence_status":"CONVERGED","decoder_hash":row["decoder_hash"],"notes":"EXPLORATORY; FAST_SPARSE_PAYLOAD"})
    fields=list(ledger[0])
    with ledger_path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fields,delimiter="\t",lineterminator="\n"); writer.writeheader(); writer.writerows(sorted(ledger,key=lambda r:r["run_id"]))
    print(json.dumps({"decision":decision,"best_selector":best_language["selector"],"language_bps":best_language["bits_per_symbol"],"matched_null_bps":matched_null["bits_per_symbol"],"gain_bits":best_language["gain_vs_matched_null_bits"]}))


if __name__ == "__main__": main()
