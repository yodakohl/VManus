#!/usr/bin/env python3
"""Validate GDT526's selected cha-stem extension."""

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
BASE = ROOT / "experiments/yolo/gdt526_cha_intermediate_stem_extension"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt526_validation.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def rank_metrics(rows, field: str) -> dict[str, int]:
    ranks = [int(row[field]) for row in rows]
    generated = [rank for rank in ranks if rank > 0]
    return {
        "target_count": len(ranks),
        "truth_generated_count": len(generated),
        "top1_exact_count": sum(rank == 1 for rank in generated),
        "top2_exact_count": sum(rank <= 2 for rank in generated),
        "top3_exact_count": sum(rank <= 3 for rank in generated),
        "top5_exact_count": sum(rank <= 5 for rank in generated),
        "rank_sum": sum(generated),
        "deepest_truth_rank": max(generated, default=0),
    }


def main() -> int:
    result = json.loads((OUT / "gdt526_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt526_1558_four_fold_cha_rehearsal.tsv")
    current = read_tsv("gdt526_159_cha_rerank.tsv")
    candidates = read_tsv("gdt526_candidate_score_atlas.tsv")
    routes = read_tsv("gdt526_cha_route_atlas.tsv")
    ladder = read_tsv("gdt526_model_ladder.tsv")
    changed = read_tsv("gdt526_changed_decision_atlas.tsv")
    remaining = read_tsv("gdt526_revised_remaining_top1_error_atlas.tsv")
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_CHA_STEM_UNSEEN_RIGHT_EXTENSION_LICENSE",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_CHA_STEM_EXTENSION__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        result["claim_ceiling"],
    )
    expected_policy = {
        "stage": "BP1_W080",
        "feature": "BONUS_PLUS_ONE",
        "weight": 0.8,
        "base": "cha=CH+A_ADDR",
        "activation": "UNSEEN_RIGHT_SUFFIX_WITH_POSITIVE_RIGHT_VISIBLE_TO_ATOM_LICENSE",
        "conflict": "OLD_EXACT_CHA_EXTENSION_OVERRIDES_STEM_DEFAULT",
    }
    check("selected_policy", result["selected_policy"] == expected_policy, result["selected_policy"])
    check("rehearsal_count", len(rehearsal) == 1558, len(rehearsal))
    check(
        "rehearsal_unique",
        len({row["surface"] for row in rehearsal}) == 1558,
        len({row["surface"] for row in rehearsal}),
    )
    check(
        "fold_counts",
        Counter(row["fold"] for row in rehearsal)
        == Counter({"0": 373, "1": 402, "2": 421, "3": 362}),
        dict(Counter(row["fold"] for row in rehearsal)),
    )
    expected_old = {
        "target_count": 1558,
        "truth_generated_count": 1441,
        "top1_exact_count": 1098,
        "top2_exact_count": 1328,
        "top3_exact_count": 1386,
        "top5_exact_count": 1418,
        "rank_sum": 2109,
        "deepest_truth_rank": 22,
    }
    old_base = rank_metrics(rehearsal, "gdt525_rank")
    old_selected = rank_metrics(rehearsal, "gdt526_rank")
    check("old_base_exact", old_base == expected_old, old_base)
    check("old_selected_exact", old_selected == expected_old, old_selected)
    check(
        "result_old_metrics",
        result["old26_four_fold_gdt525_metrics"] == expected_old
        and result["old26_four_fold_gdt526_metrics"] == expected_old,
        "both old metric blocks",
    )
    check("current_count", len(current) == 159, len(current))
    expected_inherited_base = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 145,
        "top2_exact_count": 154,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 184,
        "deepest_truth_rank": 9,
    }
    expected_inherited_selected = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 147,
        "top2_exact_count": 155,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 181,
        "deepest_truth_rank": 9,
    }
    expected_revised_base = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 146,
        "top2_exact_count": 154,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 183,
        "deepest_truth_rank": 9,
    }
    expected_revised_selected = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 148,
        "top2_exact_count": 155,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 180,
        "deepest_truth_rank": 9,
    }
    inherited_base = rank_metrics(current, "gdt525_rank")
    inherited_selected = rank_metrics(current, "gdt526_rank")
    revised_base = rank_metrics(current, "gdt525_revised_rank")
    revised_selected = rank_metrics(current, "gdt526_revised_rank")
    check("inherited_base", inherited_base == expected_inherited_base, inherited_base)
    check(
        "inherited_selected",
        inherited_selected == expected_inherited_selected,
        inherited_selected,
    )
    check("revised_base", revised_base == expected_revised_base, revised_base)
    check(
        "revised_selected",
        revised_selected == expected_revised_selected,
        revised_selected,
    )
    check(
        "result_current_metrics",
        result["current_inherited_gdt525_metrics"] == expected_inherited_base
        and result["current_inherited_gdt526_metrics"] == expected_inherited_selected
        and result["current_revised_gdt525_metrics"] == expected_revised_base
        and result["current_revised_gdt526_metrics"] == expected_revised_selected,
        "four current metric blocks",
    )
    transitions = Counter(row["decision_change_class"] for row in current)
    expected_transitions = Counter(
        {
            "GDT525_CORRECT_PRESERVED": 145,
            "GDT525_ERROR_CORRECTED": 2,
            "GDT525_ERROR_UNCHANGED": 12,
        }
    )
    check("decision_transitions", transitions == expected_transitions, dict(transitions))
    check(
        "changed_surfaces",
        {row["surface"] for row in changed} == {"chady", "chap"}
        and result["changed_surfaces"] == ["chady", "chap"],
        sorted(row["surface"] for row in changed),
    )
    expected_recipes = {"chady": "CH+A_ADDR+DY", "chap": "CH+A_ADDR+P"}
    check(
        "changed_recipes",
        {row["surface"]: row["gdt526_top1"] for row in changed} == expected_recipes,
        {row["surface"]: row["gdt526_top1"] for row in changed},
    )
    check(
        "no_current_loss",
        all(row["decision_change_class"] != "GDT525_CORRECT_LOST" for row in current),
        dict(transitions),
    )
    check(
        "score_formula",
        all(
            math.isclose(
                float(row["truth_gdt526_score"]),
                float(row["truth_gdt525_score"])
                - 0.8 * float(row["truth_cha_feature"]),
                abs_tol=2e-8,
            )
            and math.isclose(
                float(row["top1_gdt526_score"]),
                float(row["top1_gdt525_score"])
                - 0.8 * float(row["top1_cha_feature"]),
                abs_tol=2e-8,
            )
            for row in current
        ),
        "gdt526 = gdt525 - 0.8*feature",
    )
    check("route_count", len(routes) == result["current_route_count"] == 2, len(routes))
    expected_routes = {
        "chady": ("dy", "DY", "32", "52", "1.557417452"),
        "chap": ("p", "P", "2", "2", "1.550000000"),
    }
    observed_routes = {
        row["surface"]: (
            row["suffix"],
            row["atom_insert"],
            row["signature_support"],
            row["visible_condition_total"],
            row["cha_feature"],
        )
        for row in routes
    }
    check(
        "exact_routes",
        observed_routes == expected_routes
        and all(row["base_surface"] == "cha" and row["base_recipe"] == "CH+A_ADDR" for row in routes),
        observed_routes,
    )
    check(
        "routes_are_truth",
        all(row["candidate_is_truth"] == "YES" and row["gdt526_rank"] == "1" for row in routes),
        [row["surface"] for row in routes],
    )
    check(
        "remaining_count",
        len(remaining) == result["revised_remaining_top1_error_count"] == 11,
        len(remaining),
    )
    check(
        "corrected_removed_from_queue",
        not {"chady", "chap"} & {row["surface"] for row in remaining},
        sorted(row["surface"] for row in remaining),
    )
    ladder_by = {(row["scope"], row["model_stage"]): row for row in ladder}
    selected_rows = [
        ladder_by[("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", "BP1_W080")],
        ladder_by[("CURRENT_159_OLD26_TO_NEW4", "BP1_W080")],
        ladder_by[("CURRENT_159_FAMILY_REVISED", "BP1_W080")],
    ]
    check(
        "selected_ladder_rows",
        selected_rows[0]["top1_exact_count"] == "1098"
        and selected_rows[0]["rank_sum"] == "2109"
        and selected_rows[1]["top1_exact_count"] == "147"
        and selected_rows[1]["rank_sum"] == "181"
        and selected_rows[2]["top1_exact_count"] == "148"
        and selected_rows[2]["rank_sum"] == "180",
        selected_rows,
    )
    old_bp1 = [
        row for row in ladder
        if row["scope"] == "FOUR_FOLD_OLD26_SURFACE_REHEARSAL"
        and row["model_stage"].startswith("BP1_")
    ]
    check(
        "bp1_old_weight_plateau",
        len(old_bp1) == 10
        and all(row["top1_exact_count"] == "1098" and row["rank_sum"] == "2109" for row in old_bp1),
        len(old_bp1),
    )
    expected_candidate_surfaces = {
        row["surface"]
        for row in current
        if row["gdt526_rank"] != "1" or row["gdt525_top1"] != row["gdt526_top1"]
    }
    check(
        "candidate_truth_coverage",
        {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
        == expected_candidate_surfaces,
        len(expected_candidate_surfaces),
    )

    validation = {
        "experiment_id": "GDT526",
        "status": "PASS" if all(row["pass"] for row in checks) else "FAIL",
        "check_count": len(checks),
        "failed_check_count": sum(not row["pass"] for row in checks),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
