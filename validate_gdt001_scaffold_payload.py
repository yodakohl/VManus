#!/usr/bin/env python3
"""Independent CPU reconstruction of the fast shared-scaffold tournament."""

from __future__ import annotations

import hashlib
import json
import math

import numpy as np

from gdt001_core import ROOT, canonical, fixed_costs, load_lattice, sha256_file, source_symbol_count, universal_uint_bits
from gdt001_language_models import NgramLM, TARGET_LETTERS, homophone_reverse_bits, path_language_bits, source_unigrams
from gdt001_scaffold_payload import common_selected_paths, fit_scaffold_null, fit_scaffold_record, scaffold_and_payload, scaffold_rule_bits


def check(condition, name, checks):
    if not condition: raise AssertionError(name)
    checks.append(name)


def main():
    checks = []; result = json.loads((ROOT / "gdt001_scaffold_payload_results.json").read_text()); books = json.loads((ROOT / "gdt001_scaffold_payload_codebooks.json").read_text()); repair = json.loads((ROOT / "gdt001_lattice_cost_repair.json").read_text())
    check(result["schema"] == "GDT001_SCAFFOLD_PAYLOAD_RESULTS_V1", "result_schema", checks)
    check(result["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "exploratory_status", checks)
    check(result["decision"] == "STOP_NULL_PAYLOAD_WINS_LANGUAGE_KEYS_UNSTABLE", "decision", checks)
    check(result["lattice_cost_repair_sha256"] == sha256_file(ROOT / "gdt001_lattice_cost_repair.json"), "repair_hash", checks)
    check(books["language_pack_manifest_sha256"] == sha256_file(ROOT / "gdt001_language_pack_manifest.json"), "language_manifest_hash", checks)
    check(repair["all_new_candidates_same_fixed_bits"] is True and repair["all_new_candidates_same_path_digest"] is True, "common_accounting_flags", checks)
    _, lines = load_lattice(); selected = common_selected_paths(lines); common_fixed = sum(fixed_costs(selected).values()); digest = hashlib.sha256(canonical([p.path_id for p in selected])).hexdigest()
    check(abs(common_fixed - repair["repaired_common_fixed_bits"]) < 1e-8, "common_fixed_cpu", checks)
    check(digest == repair["repaired_common_selected_path_digest"], "common_path_digest_cpu", checks)
    null = fit_scaffold_null(lines); record = fit_scaffold_record(lines); by_id = {r["candidate_id"]: r for r in result["results"]}
    for reconstructed in (null, record):
        stored = by_id[reconstructed["candidate_id"]]
        check(abs(reconstructed["total_bits"] - stored["total_bits"]) < 1e-7, f"cpu_total:{reconstructed['candidate_id']}", checks)
        check(reconstructed["decoder_hash"] == stored["decoder_hash"], f"decoder_hash:{reconstructed['candidate_id']}", checks)
    scaffold_bits, payloads, scaffold = scaffold_and_payload(selected)
    frozen = books["frozen_language_lm"]; costs = np.asarray(frozen["costs_float64_flat"], dtype=np.float64).reshape(frozen["shape"]); lm = NgramLM("middle_high_german", frozen["order"], costs, frozen["corpus_letters"])
    for language in books["language_payloads"]:
        mapping_rows = language["payload_model"]["mapping"]
        mapping = [0] * 25
        for row in mapping_rows:
            if row["source_unit"] in "abcdefghijklmnopqrstuvxyz": mapping["abcdefghijklmnopqrstuvxyz".index(row["source_unit"])] = TARGET_LETTERS.index(row["latent_unit"])
        latent = scaffold_bits + sum(path_language_bits(lm, mapping, path) for path in payloads)
        reverse = homophone_reverse_bits(mapping, source_unigrams(payloads))
        key = scaffold_rule_bits() + math.log2(6) + 25 * math.log2(len(TARGET_LETTERS)) + universal_uint_bits(2)
        total = 3.0 + key + latent + reverse + common_fixed
        stored = by_id[language["candidate_id"]]
        check(abs(total - stored["total_bits"]) < 1e-7, f"cpu_total:{language['candidate_id']}", checks)
    ordered = sorted(result["results"], key=lambda row:(row["total_bits"],row["candidate_id"]))
    check(ordered == result["results"] and ordered[0]["candidate_id"] == "scaffold_null_payload_o2", "leader_order", checks)
    check(len({row["decoder_hash"] for row in result["results"] if row["model_class"] == "ABBR_LANG"}) == 3, "language_keys_unstable", checks)
    check(ordered[2]["total_bits"] - ordered[0]["total_bits"] > 300000, "language_gap_material", checks)
    validation = {"schema": "GDT001_SCAFFOLD_PAYLOAD_VALIDATION_V1", "status": "PASS_INDEPENDENT_CPU_RECONSTRUCTION", "checks": checks, "check_count": len(checks), "result_sha256": sha256_file(ROOT / "gdt001_scaffold_payload_results.json"), "codebooks_sha256": sha256_file(ROOT / "gdt001_scaffold_payload_codebooks.json"), "leader": ordered[0]["candidate_id"], "claim_ceiling": result["claim_ceiling"]}
    (ROOT / "gdt001_scaffold_payload_validation.json").write_bytes(canonical(validation)); print(json.dumps({"status": validation["status"], "checks": len(checks)}))


if __name__ == "__main__": main()
