#!/usr/bin/env python3
"""Independent CPU reconstruction and artifact-integrity validator for GDT001."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict

from gdt001_core import ROOT, LATTICE_PATH, categorical_bits, fixed_costs, load_lattice, sha256_file


def require(condition: bool, name: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def independent_ngram_bits(paths, alphabet_size: int, order: int) -> float:
    contexts = defaultdict(Counter); bos = alphabet_size
    for path in paths:
        history = [bos] * order
        for value in path.source_ids:
            contexts[tuple(history)][value] += 1
            if order: history = history[1:] + [value]
    return sum(categorical_bits([counter.get(symbol, 0) for symbol in range(alphabet_size)]) for counter in contexts.values())


def main() -> None:
    checks: list[str] = []
    summary = json.loads((ROOT / "gdt001_tournament_runs.json").read_text())
    require(summary["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "exploratory_status", checks)
    method_text = (ROOT / "GDT001_METHOD.md").read_text()
    require("confirmed" in method_text and "translation" in method_text and "NO_DECIPHERMENT_CANDIDATE_FREEZE" in method_text, "method_and_ceiling", checks)
    require(summary["lattice_sha256"] == sha256_file(LATTICE_PATH), "lattice_hash", checks)
    require(summary["language_pack_manifest_sha256"] == sha256_file(ROOT / "gdt001_language_pack_manifest.json"), "language_manifest_hash", checks)
    require(summary["gpu_benchmark_sha256"] == sha256_file(ROOT / "gdt001_gpu_benchmark.json"), "benchmark_hash", checks)
    benchmark = json.loads((ROOT / "gdt001_gpu_benchmark.json").read_text())
    require(any(row["population"] >= 32768 and row["speedup_cpu_over_cuda"] > 2.0 for row in benchmark["measurements"]), "material_cuda_crossover", checks)
    require(max(row["max_exact_score_delta_bits"] for row in benchmark["measurements"]) < 2e-6, "cpu_cuda_exact_score_agreement", checks)
    runs = summary["leaderboard"]
    require(summary["run_count"] == len(runs) and len(runs) >= 60, "run_count", checks)
    require(runs == sorted(runs, key=lambda item: (item["total_bits"], item["candidate_id"])), "leaderboard_order", checks)
    require({"ABBR_LANG", "HOMOPHONIC_CIPHER", "RECORD_NOTATION", "NONSEMANTIC_GENERATOR", "HYBRID"} <= {r["model_class"] for r in runs}, "model_classes", checks)
    _, lines = load_lattice()
    leader = json.loads((ROOT / ".gdt001/runs" / f"{runs[0]['candidate_id']}.json").read_text())
    selected = []
    for line, path_id in zip(lines, leader["selected_path_ids"]):
        selected.append(next(path for path in line.paths if path.path_id == path_id))
    exact = independent_ngram_bits(selected, 26, leader["decoder"]["order"]) + sum(fixed_costs(selected).values()) + leader["model_class_bits"] + leader["key_bits"]
    require(abs(exact - leader["total_bits"]) < 1e-7, "leader_cpu_exact_mdl", checks)
    decoder_hash = hashlib.sha256((json.dumps(leader["decoder"], sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    require(leader["decoder_hash"] == decoder_hash, "leader_decoder_hash", checks)
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open() as handle:
        ledger = list(csv.DictReader(handle, delimiter="\t"))
    require(len(ledger) == len(runs), "ledger_rows", checks)
    require({r["candidate_id"] for r in runs} == {r["run_id"] for r in ledger}, "ledger_run_ids", checks)
    controls = json.loads((ROOT / "gdt001_counterfactual_results.json").read_text())
    require(len(controls["results"]) == 20 and len({r["control"] for r in controls["results"]}) == 5, "counterfactual_matrix", checks)
    index = json.loads((ROOT / "candidates/index.json").read_text())
    require(index["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "candidate_index_status", checks)
    require(len(index["candidates"]) == 10, "ten_candidates", checks)
    breakdown = list(csv.DictReader((ROOT / "gdt001_score_breakdown.tsv").open(), delimiter="\t"))
    require({row["candidate_id"] for row in breakdown} == {item["candidate_id"] for item in index["candidates"]}, "score_breakdown_candidates", checks)
    for item in index["candidates"]:
        run = next(row for row in runs if row["candidate_id"] == item["candidate_id"])
        total = sum(float(row["accounted_total_bits"]) for row in breakdown if row["candidate_id"] == item["candidate_id"] and row["scope_type"] in {"SECTION", "GLOBAL"})
        require(abs(total - run["total_bits"]) < 1e-5, f"score_breakdown_total:{item['candidate_id']}", checks)
    edition = json.loads((ROOT / "gdt001_edition_sensitivity.json").read_text())
    require([row["edition"] for row in edition["editions"]] == ["ZL3b", "IT2a", "RF1b"], "edition_sensitivity_all_three", checks)
    required = {"model_spec.json", "mapping.tsv", "segmentation.tsv", "candidate_plaintext.tsv", "lexicon.tsv", "reverse_generation.tsv", "structural_explanation.md", "failure_analysis.md", "risky_predictions.md"}
    for item in index["candidates"]:
        directory = ROOT / "candidates" / item["candidate_id"]
        require(required <= {path.name for path in directory.iterdir()}, f"candidate_files:{item['candidate_id']}", checks)
        require(item["model_spec_sha256"] == sha256_file(directory / "model_spec.json"), f"candidate_hash:{item['candidate_id']}", checks)
        require((directory / "risky_predictions.md").read_text().count("kills this prediction") == 10, f"candidate_predictions:{item['candidate_id']}", checks)
        with (directory / "reverse_generation.tsv").open() as handle:
            reverse = list(csv.DictReader(handle, delimiter="\t"))
        require(reverse and all(row["actual_source_bits"] and row["wrong_source_bits"] for row in reverse), f"reverse_generation_scores:{item['candidate_id']}", checks)
    output = {"schema": "GDT001_TOURNAMENT_VALIDATION_V1", "status": "PASS_RECORD_AND_CPU_LEADER_RECONSTRUCTION", "checks": checks, "check_count": len(checks), "leader": runs[0]["candidate_id"], "leader_total_bits_cpu": exact}
    (ROOT / "gdt001_tournament_validation.json").write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks)}))


if __name__ == "__main__":
    main()
