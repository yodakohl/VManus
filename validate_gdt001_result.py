#!/usr/bin/env python3
"""Independent branch-wide validation of the current GDT001 result."""

import csv, json

from gdt001_core import ROOT, sha256_file


def main():
    checks = []
    def need(value, name):
        if not value: raise AssertionError(name)
        checks.append(name)
    result = json.load(open(ROOT / "gdt001_result.json"))
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open() as handle:
        ledger = list(csv.DictReader(handle, delimiter="\t"))
    converged = [row for row in ledger if row["convergence_status"] == "CONVERGED" and float(row["total_bits"]) < 1e100]
    converged.sort(key=lambda row: (float(row["total_bits"]), row["run_id"]))
    need(result["schema"] == "GDT001_YOLO_RESULT_V2", "schema")
    need(result["status"] == "EXPLORATORY_NO_CONFIRMED_TRANSLATION", "status")
    need(result["decision"] == "NO_DECIPHERMENT_CANDIDATE_FREEZE", "decision")
    need(result["run_count"] == len(ledger) and len(ledger) > 4000, "run_count")
    need(len({row["run_id"] for row in ledger}) == len(ledger), "unique_run_ids")
    need(result["converged_count"] == len(converged), "converged_count")
    need(result["failed_count"] == 4, "failed_count")
    need(result["leader"] == converged[0] and converged[0]["run_id"] == "contextmixer_s0_015625", "leader")
    for model_class in sorted({row["model_class"] for row in converged}):
        expected = next(row for row in converged if row["model_class"] == model_class)
        need(result["strongest_by_class"][model_class] == expected, f"class:{model_class}")
    need(result["candidate_export_count"] == 10 and result["fixed_packet_unique_loci"] == 199, "candidate_scope")
    need(result["inputs"] == {name: sha256_file(ROOT / name) for name in result["inputs"]}, "input_hashes")
    tournament = json.load(open(ROOT / "gdt001_tournament_runs.json"))
    need(tournament["run_count"] == len(ledger), "tournament_count")
    need(tournament["leaderboard"] == converged, "tournament_order")
    export = json.load(open(ROOT / "gdt001_candidate_export_validation.json"))
    need(export["status"] == "PASS_CURRENT_DIVERSE_TEN_PACKET_INTEGRITY", "export_validation")
    current = json.load(open(ROOT / "gdt001_current_summary_validation.json"))
    need(current["status"] == "PASS_EXPANDED_EXPLORATORY_LEDGER_AND_LEADER", "current_validation")
    mixer = json.load(open(ROOT / "gdt001_online_context_mixer_validation.json"))
    need(mixer["status"] == "PASS_CPU_EXACT_RECONSTRUCTION_CONTROL_NOT_SPECIFIC", "mixer_validation")
    with (ROOT / "gdt001_score_breakdown.tsv").open() as handle:
        breakdown = list(csv.DictReader(handle, delimiter="\t"))
    for candidate in json.load(open(ROOT / "candidates/index.json"))["candidates"]:
        total = sum(float(row["accounted_total_bits"]) for row in breakdown if row["candidate_id"] == candidate["candidate_id"] and row["scope_type"] in {"SECTION", "GLOBAL"})
        expected = json.load(open(ROOT / "candidates" / candidate["candidate_id"] / "model_spec.json"))["total_bits"]
        need(abs(total - expected) < 1e-5, f"breakdown:{candidate['candidate_id']}")
    edition = json.load(open(ROOT / "gdt001_edition_sensitivity.json"))
    need(edition["leader"] == "contextmixer_s0_015625" and [row["edition"] for row in edition["editions"]] == ["ZL3b", "IT2a", "RF1b"], "edition_scope")
    report = (ROOT / "GDT001_YOLO_RESULT.md").read_text()
    need("No translation has\nbeen obtained" in report and "No candidate qualifies" in report, "report_ceiling")
    need(f"**{len(ledger):,} retained configurations**" in report and f"**{len(converged):,} converged configurations**" in report, "report_counts")
    output = {"schema": "GDT001_RESULT_VALIDATION_V2", "status": "PASS_CURRENT_EXPLORATORY_TOURNAMENT_NO_FREEZE",
              "check_count": len(checks), "checks": checks, "run_count": len(ledger), "leader": converged[0]["run_id"],
              "claim_ceiling": "Record, hash, score-accounting, and packet validation only; no confirmed language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_result_validation.json").write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks), "runs": len(ledger)}))


if __name__ == "__main__": main()
