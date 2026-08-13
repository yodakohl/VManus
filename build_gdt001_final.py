#!/usr/bin/env python3
"""Build the current branch-wide GDT001 result and accounting summaries."""

import csv, json
from collections import defaultdict

from gdt001_core import ROOT, canonical, fixed_costs, load_lattice, sha256_file, source_symbol_count
from run_gdt001_online_context_mixer import fit


def main():
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open() as handle:
        ledger = list(csv.DictReader(handle, delimiter="\t"))
    converged = [row for row in ledger if row["convergence_status"] == "CONVERGED" and float(row["total_bits"]) < 1e100]
    converged.sort(key=lambda row: (float(row["total_bits"]), row["run_id"]))
    tournament = {"schema": "GDT001_TOURNAMENT_RUNS_V2", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
                  "serialization": "ascending paid total_bits then run_id", "run_count": len(ledger), "leaderboard": converged,
                  "lattice_sha256": sha256_file(ROOT / "gdt001_corpus_lattice.json"),
                  "language_pack_manifest_sha256": sha256_file(ROOT / "gdt001_language_pack_manifest.json"),
                  "gpu_benchmark_sha256": sha256_file(ROOT / "gdt001_gpu_benchmark.json")}
    (ROOT / "gdt001_tournament_runs.json").write_bytes(canonical(tournament))
    index = json.load(open(ROOT / "candidates/index.json"))["candidates"]; _, lines = load_lattice(); rows = []
    for item in index:
        directory = ROOT / "candidates" / item["candidate_id"]
        spec = json.load(open(directory / "model_spec.json"))
        with (directory / "segmentation.tsv").open() as handle:
            segmentation = list(csv.DictReader(handle, delimiter="\t"))
        selected = [next(path for path in line.paths if path.path_id == row["selected_path_id"]) for line, row in zip(lines, segmentation)]
        fixed = sum(fixed_costs(selected).values()); key = spec["key_bits"]; variable = spec["total_bits"] - fixed - key; total_symbols = source_symbol_count(selected)
        for kind, getter in (("CURRIER", lambda line: line.currier or "UNASSIGNED"), ("SECTION", lambda line: line.section or "UNASSIGNED")):
            buckets = defaultdict(list)
            for line, path in zip(lines, selected): buckets[getter(line)].append(path)
            for scope, paths in sorted(buckets.items()):
                symbols = source_symbol_count(paths); local_fixed = sum(fixed_costs(paths).values())
                rows.append({"candidate_id": item["candidate_id"], "scope_type": kind, "scope": scope, "source_symbols": symbols,
                             "fixed_observation_bits": local_fixed, "allocated_variable_bits": variable * symbols / total_symbols,
                             "global_model_key_bits": 0.0, "accounted_total_bits": local_fixed + variable * symbols / total_symbols,
                             "interpretation": "global variable code allocated by source-symbol count; not a refit"})
        rows.append({"candidate_id": item["candidate_id"], "scope_type": "GLOBAL", "scope": "MODEL_CLASS_AND_KEY", "source_symbols": 0,
                     "fixed_observation_bits": 0.0, "allocated_variable_bits": 0.0, "global_model_key_bits": key,
                     "accounted_total_bits": key, "interpretation": "global key and model-selection code"})
    with (ROOT / "gdt001_score_breakdown.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    editions = []
    for edition in ("ZL3b", "IT2a", "RF1b"):
        selected = []
        for line in lines:
            eligible = [path for path in line.paths if edition in path.editions] or list(line.paths)
            selected.append(min(eligible, key=lambda path: (path.fixed_bits, path.path_id)))
        score = fit(lines, selected, 1 / 64)
        editions.append({"edition": edition, "causal_mixer_total_bits": score["total_bits"], "bits_per_symbol": score["bits_per_symbol"],
                         "source_symbols": source_symbol_count(selected), "physical_lines": len(selected), "diagnostic_only": True})
    (ROOT / "gdt001_edition_sensitivity.json").write_bytes(canonical({"schema": "GDT001_EDITION_SENSITIVITY_V2", "status": "EXPLORATORY_DIAGNOSTIC_NOT_MDL_REFIT", "leader": "contextmixer_s0_015625", "evaluation": "frozen algorithm/share; causal state independently reinitialized per edition-constrained diagnostic", "editions": editions}))
    coverage = []
    for item in index:
        spec = json.load(open(ROOT / "candidates" / item["candidate_id"] / "model_spec.json"))
        coverage.append({"candidate_id": item["candidate_id"], "model_class": item["model_class"], "physical_lines": 5386,
                         "source_symbols": 194324, "full_lattice_segmentation": True, "fixed_packet_loci": 199,
                         "semantic_output": item["model_class"] in {"ABBR_LANG", "HOMOPHONIC_CIPHER", "HYBRID"},
                         "semantic_status": "POSTSELECTED_EXPLORATORY_NOT_A_READING", "paid_total_bits": spec["total_bits"]})
    (ROOT / "gdt001_structural_coverage.json").write_bytes(canonical({"schema": "GDT001_STRUCTURAL_COVERAGE_V2", "status": "EXPLORATORY", "candidates": coverage}))
    best_by_class = {}
    for row in converged:
        best_by_class.setdefault(row["model_class"], row)
    inputs = {name: sha256_file(ROOT / name) for name in ("gdt001_corpus_lattice.json", "GDT001_YOLO_LEDGER.tsv", "gdt001_tournament_runs.json", "candidates/index.json", "gdt001_candidate_export_validation.json", "gdt001_current_summary.json", "gdt001_online_context_mixer_validation.json", "gdt001_symbol_state_markov_validation.json", "gdt001_latent_space_homophonic_results.json", "gdt001_latent_space_homophonic_validation.json", "gdt001_score_breakdown.tsv", "gdt001_edition_sensitivity.json", "gdt001_structural_coverage.json")}
    result = {"schema": "GDT001_YOLO_RESULT_V2", "status": "EXPLORATORY_NO_CONFIRMED_TRANSLATION", "decision": "NO_DECIPHERMENT_CANDIDATE_FREEZE",
              "run_count": len(ledger), "converged_count": len(converged), "failed_count": len(ledger) - len(converged),
              "leader": converged[0], "strongest_by_class": best_by_class, "candidate_export_count": 10,
              "fixed_packet_unique_loci": 199, "inputs": inputs,
              "claim_ceiling": "Exploratory complete-model competition only; no confirmed translation, language, cipher, record semantics, or nonsemantic-status conclusion."}
    (ROOT / "gdt001_result.json").write_bytes(canonical(result))
    print(json.dumps({"runs": len(ledger), "leader": converged[0]["run_id"], "candidates": len(index)}))


if __name__ == "__main__": main()
