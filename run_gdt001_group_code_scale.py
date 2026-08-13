#!/usr/bin/env python3
"""Targeted scale-up of the controlled Czech whole-group character lead."""

import hashlib, json, math

from gdt001_core import ROOT, canonical, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_character_code import encoded
from run_gdt001_group_code_high_order import dense_costs, lm, search, sufficient
from run_gdt001_group_code_order4_refine import mapping_rows, refine


def one(k, seed, paths, fixed, symbols, costs, leader):
    order = 4; language = "medieval_czech"
    seqs, counts, _, vocab, _, common = encoded(paths, k)
    initial_bits, initial = search(costs, seqs, counts, k, order, seed)
    keys, frequency = sufficient(seqs, order, k); mapping, payload, trajectory = refine(costs, keys, frequency, counts, initial, order, seed)
    grid = math.log2(5) + math.log2(3); null_key = 3.0 + grid + universal_uint_bits(order) + common
    key = null_key + math.log2(5) + k * math.log2(27)
    null_payload = kt_ngram_bits(seqs, k, order); null_total = fixed + null_key + null_payload; total = fixed + key + payload
    mr = mapping_rows(mapping, vocab, counts)
    return {"k": k, "order": order, "language": language, "seed": seed, "initial_payload_bits": initial_bits,
            "total_bits": total, "bits_per_symbol": total / symbols, "matched_null_bits": null_total,
            "gain_vs_matched_null_bits": null_total - total, "gap_vs_variable_context_bits": total - leader,
            "key_bits": key, "payload_bits": payload, "fixed_bits": fixed, "coded_events": int(counts.sum()),
            "coded_runs": len(seqs), "runs_length_at_least_5": sum(len(seq) >= 5 for seq in seqs),
            "accepted_refinement_moves": len(trajectory) - 1, "decoder_hash": hashlib.sha256(canonical(mr)).hexdigest(),
            "mapping": mr, "cpu_exact": True}


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(word) for path in paths for word in path.words); costs = dense_costs(lm("medieval_czech", 4), 4)
    leader = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]["total_bits"]
    rows = [one(256, 36101, paths, fixed, symbols, costs, leader), one(512, 36102, paths, fixed, symbols, costs, leader),
            one(1024, 36103, paths, fixed, symbols, costs, leader)]
    row = min(rows, key=lambda item: item["total_bits"])
    decision = ("CONTINUE" if row["gain_vs_matched_null_bits"] > 0 else "STOP") + "_GROUP_CODE_SCALE_SINGLE_RESTART"
    output = {"schema": "GDT001_GROUP_CODE_SCALE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "decision": decision,
              "result": row, "rows": rows, "claim_ceiling": "Single-restart scale diagnostic; no group has an established character, sound, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_group_code_scale_results.json").write_bytes(canonical(output))
    print(json.dumps({"decision": decision, "result": {key: value for key, value in row.items() if key != "mapping"}}))


if __name__ == "__main__": main()
