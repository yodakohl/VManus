#!/usr/bin/env python3
"""Fast common-path scaffold/payload tournament and decisive stop rule."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from gdt001_core import ROOT, canonical, fixed_costs, load_lattice, sha256_file
from gdt001_scaffold_payload import fit_scaffold_language, fit_scaffold_null, fit_scaffold_record
from gdt001_language_models import train_pack


OUT = ROOT / "gdt001_scaffold_payload_results.json"


def main() -> None:
    _, lines = load_lattice()
    results = [fit_scaffold_null(lines), fit_scaffold_record(lines)]
    for seed in (1701, 1702, 1703): results.append(fit_scaffold_language(lines, seed))
    results.sort(key=lambda r: (r["total_bits"], r["candidate_id"]))
    null = next(r for r in results if r["candidate_id"] == "scaffold_null_payload_o2")
    languages = [r for r in results if r["model_class"] == "ABBR_LANG"]
    stable = len({r["decoder_hash"] for r in languages}) == 1
    decision = "STOP_NULL_PAYLOAD_WINS" if null["total_bits"] <= min(r["total_bits"] for r in results if r is not null) else "CONTINUE_LAYERED_PAYLOAD"
    if not stable: decision += "_LANGUAGE_KEYS_UNSTABLE"
    old_null = json.loads((ROOT / ".gdt001/runs/nonsemantic_ngram_o2.json").read_text())
    old_lang = json.loads((ROOT / ".gdt001/runs/abbr_lang_multigraph_middle_high_german_nonull_s0101.json").read_text())
    repair = {"schema": "GDT001_LATTICE_COST_REPAIR_V1", "old_null_fixed_bits": sum(old_null[k] for k in ("observation_choice_bits", "raw_residual_bits", "separator_bits")), "old_language_fixed_bits": sum(old_lang[k] for k in ("observation_choice_bits", "raw_residual_bits", "separator_bits")), "old_fixed_advantage_bits_per_source_symbol": (sum(old_lang[k] for k in ("observation_choice_bits", "raw_residual_bits", "separator_bits")) - sum(old_null[k] for k in ("observation_choice_bits", "raw_residual_bits", "separator_bits"))) / old_null["source_symbols"], "repaired_common_selected_path_digest": null["selected_path_digest"], "repaired_common_fixed_bits": null["common_fixed_bits"], "all_new_candidates_same_path_digest": len({r["selected_path_digest"] for r in results}) == 1, "all_new_candidates_same_fixed_bits": len({round(r["common_fixed_bits"], 9) for r in results}) == 1}
    (ROOT / "gdt001_lattice_cost_repair.json").write_bytes(canonical(repair))
    compact = [{k: r[k] for k in ("candidate_id", "model_class", "language_or_system", "seed", "config_hash", "total_bits", "bits_per_symbol", "key_bits", "latent_bits", "reconstruction_bits", "exception_bits", "decoder_hash", "selected_path_digest")} | {"common_fixed_bits": r["common_fixed_bits"]} for r in results]
    payload = {"schema": "GDT001_SCAFFOLD_PAYLOAD_RESULTS_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "decision": decision, "language_decoder_stable": stable, "results": compact, "lattice_cost_repair_sha256": sha256_file(ROOT / "gdt001_lattice_cost_repair.json"), "claim_ceiling": "Exploratory shared-scaffold payload comparison only; no language, plaintext, record meaning, or nonsemantic-manuscript claim."}
    OUT.write_bytes(canonical(payload))
    with (ROOT / "gdt001_scaffold_payload_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(compact[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(compact)
    scaffold = dict(results[0]["decoder"]["scaffold"]); scaffold.pop("line_programs", None)
    lm = train_pack("middle_high_german", 2)
    codebooks = {
        "schema": "GDT001_SCAFFOLD_PAYLOAD_CODEBOOKS_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
        "common_scaffold": scaffold,
        "null_payload": next(r["decoder"]["payload_model"] for r in results if r["candidate_id"] == "scaffold_null_payload_o2"),
        "record_payload": next(r["decoder"]["payload_model"] for r in results if r["candidate_id"] == "scaffold_record_payload"),
        "language_payloads": [{"candidate_id": r["candidate_id"], "seed": r["seed"], "decoder_hash": r["decoder_hash"], "payload_model": r["decoder"]["payload_model"]} for r in languages],
        "frozen_language_lm": {"language": "middle_high_german", "order": 2, "shape": list(lm.costs.shape), "costs_float64_flat": lm.costs.ravel().tolist(), "corpus_letters": lm.corpus_letters},
        "language_pack_manifest_sha256": sha256_file(ROOT / "gdt001_language_pack_manifest.json"),
    }
    (ROOT / "gdt001_scaffold_payload_codebooks.json").write_bytes(canonical(codebooks))
    map_rows = []
    for r in languages:
        for row in r["decoder"]["payload_model"]["mapping"]:
            map_rows.append({"candidate_id": r["candidate_id"], "source_unit": row["source_unit"], "latent_unit": row["latent_unit"], "probability": row["mapping_probability"], "context": row["context_restriction"], "occurrences": row["occurrences"], "reverse_ambiguity": row["reverse_ambiguity"]})
    with (ROOT / "gdt001_scaffold_payload_mapping.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(map_rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(map_rows)
    # Append/replace exact branch-local run rows without touching canonical ledgers.
    ledger_path = ROOT / "GDT001_YOLO_LEDGER.tsv"
    with ledger_path.open() as handle: ledger = list(csv.DictReader(handle, delimiter="\t"))
    ledger = [row for row in ledger if not row["run_id"].startswith("scaffold_")]
    for r in results:
        ledger.append({"run_id": r["candidate_id"], "model_class": r["model_class"], "language_or_system": r["language_or_system"], "seed": str(r["seed"]), "config_hash": r["config_hash"], "total_bits": f"{r['total_bits']:.6f}", "bits_per_symbol": f"{r['bits_per_symbol']:.9f}", "key_bits": f"{r['key_bits']:.6f}", "latent_bits": f"{r['latent_bits']:.6f}", "reconstruction_bits": f"{r['reconstruction_bits']:.6f}", "exception_bits": f"{r['exception_bits']:.6f}", "convergence_status": r["convergence_status"], "decoder_hash": r["decoder_hash"], "notes": "EXPLORATORY; FAST_SHARED_SCAFFOLD"})
    fields = list(ledger[0])
    with ledger_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(sorted(ledger, key=lambda r:r["run_id"]))
    print(json.dumps({"decision": decision, "leader": results[0]["candidate_id"], "leader_bps": results[0]["bits_per_symbol"], "language_stable": stable}))


if __name__ == "__main__": main()
