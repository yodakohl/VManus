#!/usr/bin/env python3
"""Independent consistency checks for GDT520 artifacts."""

from __future__ import annotations

import csv
import hashlib
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
OUT = ROOT / "experiments/yolo/gdt520_renderer_boundary_license_lattice/artifacts"
VALIDATION = OUT / "gdt520_validation.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def stable_fold(surface: str) -> int:
    digest = hashlib.sha256(surface.encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % 4


def metrics(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    ranks = [int(row[field]) for row in rows]
    positive = [rank for rank in ranks if rank]
    return {
        "target_count": len(rows),
        "truth_generated_count": len(positive),
        "top1_exact_count": sum(rank == 1 for rank in ranks),
        "top2_exact_count": sum(0 < rank <= 2 for rank in ranks),
        "top3_exact_count": sum(0 < rank <= 3 for rank in ranks),
        "top5_exact_count": sum(0 < rank <= 5 for rank in ranks),
        "rank_sum": sum(positive),
        "deepest_truth_rank": max(positive, default=0),
    }


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    result = json.loads((OUT / "gdt520_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt520_1558_four_fold_boundary_rehearsal.tsv")
    current = read_tsv("gdt520_159_boundary_rerank.tsv")
    candidates = read_tsv("gdt520_candidate_score_atlas.tsv")
    changed = read_tsv("gdt520_changed_decision_atlas.tsv")
    contested = read_tsv("gdt520_contested_boundary_atlas.tsv")
    remaining = read_tsv("gdt520_remaining_top1_error_atlas.tsv")
    licenses = read_tsv("gdt520_visible_boundary_license_atlas.tsv")
    ladder = read_tsv("gdt520_model_ladder.tsv")

    check(
        "result_status",
        result["status"] == "PASS_RENDERER_BOUNDARY_LICENSE_LATTICE",
        result["status"],
    )
    check(
        "claim_ceiling_exploratory",
        result["claim_ceiling"].startswith("EXPLORATORY_"),
        result["claim_ceiling"],
    )
    policy = result["selected_policy"]
    check(
        "selected_weights",
        policy["segment_count_weight"] == 0.1 and policy["boundary_weight"] == 0.1,
        [policy["segment_count_weight"], policy["boundary_weight"]],
    )

    check("rehearsal_count", len(rehearsal) == 1558, len(rehearsal))
    check(
        "rehearsal_surface_unique",
        len({row["surface"] for row in rehearsal}) == 1558,
        len({row["surface"] for row in rehearsal}),
    )
    observed_folds = Counter(row["fold"] for row in rehearsal)
    check(
        "fold_counts",
        observed_folds == Counter({"0": 373, "1": 402, "2": 421, "3": 362}),
        dict(observed_folds),
    )
    check(
        "fold_hash_assignment",
        all(int(row["fold"]) == stable_fold(row["surface"]) for row in rehearsal),
        "all rows",
    )
    check(
        "rehearsal_generated",
        sum(row["truth_generated"] == "YES" for row in rehearsal) == 1441,
        sum(row["truth_generated"] == "YES" for row in rehearsal),
    )
    old_base = metrics(rehearsal, "gdt519_rank")
    old_selected = metrics(rehearsal, "gdt520_rank")
    check(
        "old_base_exact",
        old_base == result["old26_four_fold_gdt519_metrics"],
        old_base,
    )
    check(
        "old_selected_exact",
        old_selected == result["old26_four_fold_gdt520_metrics"],
        old_selected,
    )
    check("old_base_top1", old_base["top1_exact_count"] == 1082, old_base["top1_exact_count"])
    check("old_selected_top1", old_selected["top1_exact_count"] == 1089, old_selected["top1_exact_count"])
    check("old_selected_top3", old_selected["top3_exact_count"] == 1381, old_selected["top3_exact_count"])
    check("old_selected_rank_sum", old_selected["rank_sum"] == 2139, old_selected["rank_sum"])
    check("old_selected_deepest", old_selected["deepest_truth_rank"] == 22, old_selected["deepest_truth_rank"])

    check("current_count", len(current) == 159, len(current))
    check(
        "current_surface_unique",
        len({row["surface"] for row in current}) == 159,
        len({row["surface"] for row in current}),
    )
    current_base = metrics(current, "gdt519_rank")
    current_selected = metrics(current, "gdt520_rank")
    check("current_base_exact", current_base == result["current_gdt519_metrics"], current_base)
    check("current_selected_exact", current_selected == result["current_gdt520_metrics"], current_selected)
    check("current_base_top1", current_base["top1_exact_count"] == 138, current_base["top1_exact_count"])
    check("current_selected_top1", current_selected["top1_exact_count"] == 139, current_selected["top1_exact_count"])
    check("current_selected_top2", current_selected["top2_exact_count"] == 154, current_selected["top2_exact_count"])
    check("current_selected_top3", current_selected["top3_exact_count"] == 158, current_selected["top3_exact_count"])
    check("current_selected_top5", current_selected["top5_exact_count"] == 158, current_selected["top5_exact_count"])
    check("current_selected_rank_sum", current_selected["rank_sum"] == 190, current_selected["rank_sum"])
    check("current_selected_deepest", current_selected["deepest_truth_rank"] == 9, current_selected["deepest_truth_rank"])
    classes = Counter(row["decision_change_class"] for row in current)
    check(
        "decision_classes",
        dict(sorted(classes.items())) == result["current_decision_change_classes"],
        dict(classes),
    )
    check("corrected_count", classes["GDT519_ERROR_CORRECTED"] == 2, classes["GDT519_ERROR_CORRECTED"])
    check("lost_count", classes["GDT519_CORRECT_LOST"] == 1, classes["GDT519_CORRECT_LOST"])
    check(
        "changed_surfaces",
        {row["surface"] for row in changed} == {"chekeey", "psheody", "shckheody"},
        sorted(row["surface"] for row in changed),
    )
    check("remaining_count", len(remaining) == 20, len(remaining))
    check(
        "remaining_exact",
        {row["surface"] for row in remaining}
        == {row["surface"] for row in current if row["gdt520_rank"] != "1"},
        len(remaining),
    )
    check(
        "top1_matches_top5",
        all(row["gdt520_top1"] == row["gdt520_top5"].split(" | ")[0] for row in current),
        "all rows",
    )
    check(
        "truth_top1_consistency",
        all((row["gdt520_rank"] == "1") == (row["truth_recipe"] == row["gdt520_top1"]) for row in current),
        "all rows",
    )
    check(
        "score_formula_truth",
        all(
            abs(
                float(row["truth_gdt520_score"])
                - float(row["truth_gdt519_score"])
                - 0.1 * int(row["truth_segment_count"])
                - 0.1 * float(row["truth_boundary_nll"])
            ) < 3e-8
            for row in current
        ),
        "weight 0.1 + 0.1",
    )
    check(
        "score_formula_top1",
        all(
            abs(
                float(row["top1_gdt520_score"])
                - float(row["top1_gdt519_score"])
                - 0.1 * int(row["top1_segment_count"])
                - 0.1 * float(row["top1_boundary_nll"])
            ) < 3e-8
            for row in current
        ),
        "weight 0.1 + 0.1",
    )
    numeric = [
        float(row[field])
        for row in current
        for field in (
            "truth_gdt519_score", "truth_boundary_nll", "truth_gdt520_score",
            "top1_gdt519_score", "top1_boundary_nll", "top1_gdt520_score",
        )
    ]
    check("scores_finite", all(math.isfinite(value) for value in numeric), len(numeric))
    check("scores_nonnegative", min(numeric) >= 0, min(numeric))
    check(
        "alignment_traces_present",
        all("=>" in row["truth_alignment_trace"] and "~" in row["top1_alignment_trace"] for row in current),
        "all rows",
    )

    pair_rows = [row for row in licenses if row["license_level"] == "PAIR"]
    window_rows = [row for row in licenses if row["license_level"] == "FOUR_CHAR_WINDOW"]
    check("license_row_count", len(licenses) == 2236, len(licenses))
    check("pair_license_count", len(pair_rows) == 199, len(pair_rows))
    check("window_license_count", len(window_rows) == 2037, len(window_rows))
    check(
        "license_counts_match_policy",
        len(pair_rows) == policy["visible_pair_license_count"]
        and len(window_rows) == policy["visible_window_license_count"],
        [len(pair_rows), len(window_rows)],
    )
    check(
        "boundary_slot_count",
        sum(int(row["contact_count"]) for row in pair_rows) == 7433,
        sum(int(row["contact_count"]) for row in pair_rows),
    )
    pair_probabilities = [float(row["smoothed_open_probability"]) for row in pair_rows]
    window_probabilities = [float(row["smoothed_open_probability"]) for row in window_rows]
    check(
        "pair_probability_unit_interval",
        min(pair_probabilities) > 0 and max(pair_probabilities) < 1,
        [min(pair_probabilities), max(pair_probabilities)],
    )
    check(
        "final_window_probability_bounds",
        min(window_probabilities) >= 0.02 and max(window_probabilities) <= 0.98,
        [min(window_probabilities), max(window_probabilities)],
    )
    check(
        "contact_partition",
        all(
            int(row["contact_count"])
            == int(row["open_boundary_count"]) + int(row["closed_renderer_count"])
            for row in licenses
        ),
        "all rows",
    )
    check("candidate_count", len(candidates) == 238, len(candidates))
    check("contested_count", len(contested) == 22, len(contested))
    check(
        "candidate_truth_coverage",
        {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
        == {row["surface"] for row in current if row["gdt520_rank"] != "1" or row["gdt519_top1"] != row["gdt520_top1"]},
        len({row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}),
    )
    check("ladder_count", len(ladder) == 16, len(ladder))
    selected_old = next(
        row for row in ladder
        if row["scope"] == "FOUR_FOLD_OLD26_SURFACE_REHEARSAL"
        and row["model_stage"] == "GDT520_SELECTED"
    )
    selected_current = next(
        row for row in ladder
        if row["scope"] == "CURRENT_159_OLD26_TO_NEW4"
        and row["model_stage"] == "GDT520_SELECTED"
    )
    check(
        "ladder_selected_old",
        selected_old["top1_exact_count"] == "1089" and selected_old["rank_sum"] == "2139",
        [selected_old["top1_exact_count"], selected_old["rank_sum"]],
    )
    check(
        "ladder_selected_current",
        selected_current["top1_exact_count"] == "139" and selected_current["rank_sum"] == "190",
        [selected_current["top1_exact_count"], selected_current["rank_sum"]],
    )
    check(
        "known_precedence",
        all(row["working_policy"].startswith("KNOWN_EVENT_OR_SURFACE_RECIPE_STILL_WINS") for row in current),
        "all rows",
    )
    check(
        "sealed_pages_absent",
        all("f84" not in row["physical_pages"] for row in current),
        "all current page fields",
    )

    failed = [row for row in checks if not row["pass"]]
    validation = {
        "experiment_id": "GDT520",
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
