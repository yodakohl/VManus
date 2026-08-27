#!/usr/bin/env python3
"""Independent consistency checks for GDT518 compact artifacts."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
OUT = ROOT / "experiments/yolo/gdt518_context_aware_surface_recipe_reranker/artifacts"
VALIDATION = OUT / "gdt518_validation.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    result = json.loads((OUT / "gdt518_result.json").read_text(encoding="utf-8"))
    rows = read_tsv("gdt518_159_context_rerank.tsv")
    baseline = read_tsv("gdt518_42_baseline_disagreement_atlas.tsv")
    remaining = read_tsv("gdt518_remaining_top1_error_atlas.tsv")
    changed = read_tsv("gdt518_changed_decision_atlas.tsv")
    candidates = read_tsv("gdt518_candidate_cost_atlas.tsv")
    ladder = read_tsv("gdt518_model_ladder.tsv")

    check("result_status", result["status"] == "PASS_CONTEXT_AWARE_SURFACE_RECIPE_RERANKER", result["status"])
    check("claim_ceiling_exploratory", result["claim_ceiling"].startswith("EXPLORATORY_"), result["claim_ceiling"])
    check("target_row_count", len(rows) == 159, len(rows))
    check("surface_unique", len({row["surface"] for row in rows}) == 159, len({row["surface"] for row in rows}))
    check("baseline_disagreement_count", len(baseline) == 42, len(baseline))
    check("remaining_error_count", len(remaining) == 25, len(remaining))
    check("changed_decision_count", len(changed) == 31, len(changed))
    check("model_ladder_count", len(ladder) == 6, len(ladder))
    check("all_truth_generated_baseline", all(int(row["baseline_rank"]) > 0 for row in rows), "159 expected")
    check("all_truth_generated_selected", all(int(row["selected_rank"]) > 0 for row in rows), "159 expected")
    check("candidate_cap_respected", max(int(row["candidate_count_capped"]) for row in rows) <= 100, max(int(row["candidate_count_capped"]) for row in rows))
    check("baseline_top1_count", sum(row["baseline_rank"] == "1" for row in rows) == 117, sum(row["baseline_rank"] == "1" for row in rows))
    check("baseline_top5_count", sum(int(row["baseline_rank"]) <= 5 for row in rows) == 157, sum(int(row["baseline_rank"]) <= 5 for row in rows))
    check("selected_top1_count", sum(row["selected_rank"] == "1" for row in rows) == 134, sum(row["selected_rank"] == "1" for row in rows))
    check("selected_top2_count", sum(int(row["selected_rank"]) <= 2 for row in rows) == 147, sum(int(row["selected_rank"]) <= 2 for row in rows))
    check("selected_top3_count", sum(int(row["selected_rank"]) <= 3 for row in rows) == 155, sum(int(row["selected_rank"]) <= 3 for row in rows))
    check("selected_top5_count", sum(int(row["selected_rank"]) <= 5 for row in rows) == 158, sum(int(row["selected_rank"]) <= 5 for row in rows))
    check("selected_rank_sum", sum(int(row["selected_rank"]) for row in rows) == 212, sum(int(row["selected_rank"]) for row in rows))
    check("selected_deepest_rank", max(int(row["selected_rank"]) for row in rows) == 14, max(int(row["selected_rank"]) for row in rows))
    check("net_top1_gain", result["net_top1_gain"] == 17, result["net_top1_gain"])
    observed_classes = Counter(row["decision_change_class"] for row in rows)
    check("change_classes_match", dict(sorted(observed_classes.items())) == result["decision_change_classes"], dict(observed_classes))
    check("corrected_count", observed_classes["BASELINE_ERROR_CORRECTED"] == 22, observed_classes["BASELINE_ERROR_CORRECTED"])
    check("lost_count", observed_classes["BASELINE_CORRECT_LOST"] == 5, observed_classes["BASELINE_CORRECT_LOST"])
    check("changed_rows_exact", {row["surface"] for row in changed} == {row["surface"] for row in rows if row["baseline_top1"] != row["selected_top1"]}, len(changed))
    check("baseline_rows_exact", {row["surface"] for row in baseline} == {row["surface"] for row in rows if row["baseline_rank"] != "1"}, len(baseline))
    check("remaining_rows_exact", {row["surface"] for row in remaining} == {row["surface"] for row in rows if row["selected_rank"] != "1"}, len(remaining))
    check("top1_matches_first_top5", all(row["selected_top1"] == row["selected_top5"].split(" | ")[0] for row in rows), "all rows")
    check("truth_top1_consistency", all((row["selected_rank"] == "1") == (row["truth_recipe"] == row["selected_top1"]) for row in rows), "all rows")
    numeric_fields = [
        "truth_structural_cost", "truth_bigram_nll", "truth_trigram_nll",
        "truth_selected_score", "top1_structural_cost", "top1_bigram_nll",
        "top1_trigram_nll", "top1_selected_score",
    ]
    numeric_values = [float(row[field]) for row in rows for field in numeric_fields]
    check("costs_finite", all(math.isfinite(value) for value in numeric_values), len(numeric_values))
    check("costs_nonnegative", all(value >= 0 for value in numeric_values), min(numeric_values))
    check("candidate_rows_present", len(candidates) == 662, len(candidates))
    truth_candidate_surfaces = {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
    expected_candidate_surfaces = {row["surface"] for row in rows if row["selected_rank"] != "1" or row["baseline_rank"] != row["selected_rank"]}
    check("candidate_truth_coverage", truth_candidate_surfaces == expected_candidate_surfaces, len(truth_candidate_surfaces))
    check("candidate_selected_rank_unique", len({(row["surface"], row["selected_rank"]) for row in candidates}) == len(candidates), len(candidates))
    ladder_by_stage = {row["model_stage"]: row for row in ladder}
    check("ladder_baseline_top1", ladder_by_stage["GDT517_ORIGINAL"]["top1_exact_count"] == "117", ladder_by_stage["GDT517_ORIGINAL"]["top1_exact_count"])
    check("ladder_surface_top1", ladder_by_stage["RIDGE_PLUS_BASE_RANK"]["top1_exact_count"] == "133", ladder_by_stage["RIDGE_PLUS_BASE_RANK"]["top1_exact_count"])
    check("ladder_selected_top1", ladder_by_stage["SELECTED_BIGRAM_TRIGRAM_MEAN"]["top1_exact_count"] == "134", ladder_by_stage["SELECTED_BIGRAM_TRIGRAM_MEAN"]["top1_exact_count"])
    check("context_positive_weight", result["selection"]["context_weight"] > 0, result["selection"]["context_weight"])
    check("no_context_count", sum(row["prose_context_occurrence_count"] == "0" for row in rows) == 14, sum(row["prose_context_occurrence_count"] == "0" for row in rows))
    check("known_precedence_unchanged", all(row["working_policy"].startswith("EXACT_EVENT_OR_KNOWN_SURFACE_STILL_WINS") for row in rows), "all rows")
    check("sealed_pages_absent", all("f84" not in row["physical_pages"] for row in rows), "all target page fields")

    failed = [row for row in checks if not row["pass"]]
    validation = {
        "experiment_id": "GDT518",
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
