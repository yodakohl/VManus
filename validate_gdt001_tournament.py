#!/usr/bin/env python3
"""Independent current-ledger and diverse-candidate tournament validation."""

import csv
import json

from gdt001_core import ROOT, sha256_file


def main():
    checks = []

    def need(value, name):
        if not value:
            raise AssertionError(name)
        checks.append(name)

    tournament = json.load(open(ROOT / "gdt001_tournament_runs.json"))
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open() as handle:
        ledger = list(csv.DictReader(handle, delimiter="\t"))
    converged = [row for row in ledger if row["convergence_status"] == "CONVERGED" and float(row["total_bits"]) < 1e100]
    converged.sort(key=lambda row: (float(row["total_bits"]), row["run_id"]))
    need(tournament["schema"] == "GDT001_TOURNAMENT_RUNS_V2", "schema")
    need(tournament["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "status")
    need(tournament["run_count"] == len(ledger) and len(ledger) > 4000, "run_count")
    need(len({row["run_id"] for row in ledger}) == len(ledger), "unique_run_ids")
    need(tournament["leaderboard"] == converged, "complete_ordered_ledger")
    need(converged[0]["run_id"] == "contextmixer_s0_015625", "current_leader")
    need({"ABBR_LANG", "HOMOPHONIC_CIPHER", "RECORD_NOTATION", "NONSEMANTIC_GENERATOR", "HYBRID"} <= {row["model_class"] for row in converged}, "required_classes")
    need(tournament["lattice_sha256"] == sha256_file(ROOT / "gdt001_corpus_lattice.json"), "lattice_hash")
    need(tournament["language_pack_manifest_sha256"] == sha256_file(ROOT / "gdt001_language_pack_manifest.json"), "language_manifest_hash")
    need(tournament["gpu_benchmark_sha256"] == sha256_file(ROOT / "gdt001_gpu_benchmark.json"), "gpu_benchmark_hash")
    mixer = json.load(open(ROOT / "gdt001_online_context_mixer_validation.json"))
    need(mixer["status"] == "PASS_CPU_EXACT_RECONSTRUCTION_CONTROL_NOT_SPECIFIC", "cpu_exact_leader")
    need(abs(float(converged[0]["total_bits"]) - mixer["total_bits"]) < 1e-5, "leader_total")
    export = json.load(open(ROOT / "gdt001_candidate_export_validation.json"))
    need(export["status"] == "PASS_CURRENT_DIVERSE_TEN_PACKET_INTEGRITY", "candidate_export")
    index = json.load(open(ROOT / "candidates/index.json"))
    need(len(index["candidates"]) == 10, "ten_candidates")
    need(index["candidates"][0]["candidate_id"] == "contextmixer_s0_015625", "leader_exported")
    need(export["packet_unique_loci"] == 199, "fixed_packet_unique")
    latent = json.load(open(ROOT / "gdt001_latent_space_homophonic_validation.json"))
    need(latent["status"] == "PASS_EXACT_ARTIFACT_ARITHMETIC_DECISIVE_SCREEN_STOP", "latent_space_stop")
    skeleton = json.load(open(ROOT / "gdt001_consonantal_skeleton_validation.json"))
    need(skeleton["status"] == "PASS_INDEPENDENT_PYTHON_PROJECTED_KEY_DIAGNOSTIC", "consonantal_skeleton_projected_key")
    line_initial = json.load(open(ROOT / "gdt001_line_initial_channel_validation.json"))
    need(line_initial["status"] == "PASS_INDEPENDENT_CPU_EXACT_STOP", "line_initial_stop")
    frozen_keys = json.load(open(ROOT / "gdt001_frozen_line_state_keys_validation.json"))
    need(frozen_keys["status"] == "PASS_INDEPENDENT_CPU_EXACT_STOP", "frozen_line_keys_stop")
    mtf = json.load(open(ROOT / "gdt001_mtf_dynamic_rank_validation.json"))
    need(mtf["status"] == "PASS_INDEPENDENT_PYTHON_EXACT_STOP", "mtf_dynamic_rank_stop")
    symbol = json.load(open(ROOT / "gdt001_symbol_state_markov_validation.json"))
    need(symbol["status"] == "PASS_EXACT_ARTIFACT_ARITHMETIC_STOP", "symbol_state_stop")
    report = (ROOT / "GDT001_YOLO_RESULT.md").read_text()
    need("No translation has\nbeen obtained" in report, "report_ceiling")
    output = {"schema": "GDT001_TOURNAMENT_VALIDATION_V2", "status": "PASS_CURRENT_LEDGER_PACKET_AND_CPU_LEADER",
              "check_count": len(checks), "checks": checks, "run_count": len(ledger), "converged_count": len(converged),
              "leader": converged[0]["run_id"], "leader_total_bits": float(converged[0]["total_bits"]),
              "claim_ceiling": "Tournament, packet, and CPU-source-code validation only; no language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_tournament_validation.json").write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks), "runs": len(ledger)}))


if __name__ == "__main__":
    main()
