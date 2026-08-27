#!/usr/bin/env python3
"""Independent consistency checks for GDT522 artifacts."""

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
OUT = ROOT / "experiments/yolo/gdt522_local_edit_analogy_license_reranker/artifacts"
VALIDATION = OUT / "gdt522_validation.json"


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

    result = json.loads((OUT / "gdt522_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt522_1558_four_fold_local_analogy_rehearsal.tsv")
    current = read_tsv("gdt522_159_local_analogy_rerank.tsv")
    candidates = read_tsv("gdt522_candidate_score_atlas.tsv")
    changed = read_tsv("gdt522_changed_decision_atlas.tsv")
    remaining = read_tsv("gdt522_remaining_top1_error_atlas.tsv")
    analogies = read_tsv("gdt522_local_edit_analogy_atlas.tsv")
    nullable = read_tsv("gdt522_nullable_visible_edit_atlas.tsv")
    folds = read_tsv("gdt522_fold_model_inventory.tsv")
    ladder = read_tsv("gdt522_model_ladder.tsv")

    check(
        "result_status",
        result["status"] == "PASS_NEAREST_LOCAL_EDIT_ANALOGY_LICENSE",
        result["status"],
    )
    check(
        "claim_ceiling_exploratory",
        result["claim_ceiling"].startswith("EXPLORATORY_"),
        result["claim_ceiling"],
    )
    policy = result["selected_policy"]
    check(
        "selected_policy",
        policy["stage"] == "COND_C110_W040"
        and policy["missing_relation_cost"] == 1.1
        and policy["analogy_weight"] == 0.4
        and policy["max_visible_insert"] == 3
        and policy["max_atom_insert"] == 3
        and policy["conditional_alpha"] == 0.5
        and policy["reliability_prior"] == 2.0,
        policy,
    )
    check(
        "direction_and_nearest_base",
        policy["target_orientation"] == "TARGET_IS_BIG_FORM_ONLY"
        and policy["base_selection"] == "MINIMUM_VISIBLE_DELETION_LENGTH",
        [policy["target_orientation"], policy["base_selection"]],
    )
    check(
        "unique_pair_and_null_policy",
        policy["pair_counting"] == "UNIQUE_BIG_SMALL_SIGNATURE"
        and policy["equal_recipe_policy"]
        == "VISIBLE_INSERT_MAPS_TO_NULL_ATOM_INSERT",
        [policy["pair_counting"], policy["equal_recipe_policy"]],
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
        "generated_count",
        sum(row["truth_generated"] == "YES" for row in rehearsal) == 1441,
        sum(row["truth_generated"] == "YES" for row in rehearsal),
    )
    old_base = metrics(rehearsal, "gdt521_rank")
    old_selected = metrics(rehearsal, "gdt522_rank")
    check(
        "old_base_exact",
        old_base == result["old26_four_fold_gdt521_metrics"],
        old_base,
    )
    check(
        "old_selected_exact",
        old_selected == result["old26_four_fold_gdt522_metrics"],
        old_selected,
    )
    check(
        "old_selected_expected",
        old_selected
        == {
            "target_count": 1558,
            "truth_generated_count": 1441,
            "top1_exact_count": 1096,
            "top2_exact_count": 1327,
            "top3_exact_count": 1386,
            "top5_exact_count": 1418,
            "rank_sum": 2113,
            "deepest_truth_rank": 22,
        },
        old_selected,
    )
    old_classes = Counter()
    for row in rehearsal:
        old_rank = int(row["gdt521_rank"])
        new_rank = int(row["gdt522_rank"])
        if old_rank == 1 and new_rank == 1:
            old_classes["CORRECT_PRESERVED"] += 1
        elif old_rank != 1 and new_rank == 1:
            old_classes["ERROR_CORRECTED"] += 1
        elif old_rank == 1 and new_rank != 1:
            old_classes["CORRECT_LOST"] += 1
    check(
        "old_top1_transitions",
        old_classes["ERROR_CORRECTED"] == 14
        and old_classes["CORRECT_LOST"] == 8,
        dict(old_classes),
    )

    check("current_count", len(current) == 159, len(current))
    check(
        "current_surface_unique",
        len({row["surface"] for row in current}) == 159,
        len({row["surface"] for row in current}),
    )
    current_base = metrics(current, "gdt521_rank")
    current_selected = metrics(current, "gdt522_rank")
    check(
        "current_base_exact",
        current_base == result["current_gdt521_metrics"],
        current_base,
    )
    check(
        "current_selected_exact",
        current_selected == result["current_gdt522_metrics"],
        current_selected,
    )
    check(
        "current_selected_expected",
        current_selected
        == {
            "target_count": 159,
            "truth_generated_count": 159,
            "top1_exact_count": 142,
            "top2_exact_count": 154,
            "top3_exact_count": 158,
            "top5_exact_count": 158,
            "rank_sum": 187,
            "deepest_truth_rank": 9,
        },
        current_selected,
    )
    classes = Counter(row["decision_change_class"] for row in current)
    check(
        "decision_classes",
        dict(sorted(classes.items())) == result["current_decision_change_classes"],
        dict(classes),
    )
    check(
        "current_no_loss",
        classes["GDT521_ERROR_CORRECTED"] == 2
        and classes["GDT521_CORRECT_LOST"] == 0,
        dict(classes),
    )
    check(
        "changed_surfaces",
        {row["surface"] for row in changed} == {"dcheol", "dyky"},
        sorted(row["surface"] for row in changed),
    )
    corrections = {row["surface"]: row["gdt522_top1"] for row in changed}
    check(
        "corrected_recipes",
        corrections
        == {
            "dcheol": "D_ADDR+CH+E+O+L",
            "dyky": "D_ADDR+Y+K+Y",
        },
        corrections,
    )
    check("remaining_count", len(remaining) == 17, len(remaining))
    check(
        "remaining_exact",
        {row["surface"] for row in remaining}
        == {row["surface"] for row in current if row["gdt522_rank"] != "1"},
        len(remaining),
    )
    check(
        "top1_matches_top5",
        all(row["gdt522_top1"] == row["gdt522_top5"].split(" | ")[0] for row in current),
        "all rows",
    )
    check(
        "truth_top1_consistency",
        all(
            (row["gdt522_rank"] == "1")
            == (row["truth_recipe"] == row["gdt522_top1"])
            for row in current
        ),
        "all rows",
    )
    check(
        "score_formula_truth",
        all(
            abs(
                float(row["truth_gdt522_score"])
                - float(row["truth_gdt521_score"])
                + 0.4 * float(row["truth_analogy_bonus"])
            )
            < 2e-8
            for row in current
        ),
        "gdt521 - 0.4 * bonus",
    )
    check(
        "score_formula_top",
        all(
            abs(
                float(row["top1_gdt522_score"])
                - float(row["top1_gdt521_score"])
                + 0.4 * float(row["top1_analogy_bonus"])
            )
            < 2e-8
            for row in current
        ),
        "gdt521 - 0.4 * bonus",
    )
    numeric = [
        float(row[field])
        for row in current
        for field in (
            "truth_gdt521_score", "truth_analogy_bonus", "truth_gdt522_score",
            "top1_gdt521_score", "top1_analogy_bonus", "top1_gdt522_score",
        )
    ]
    check("scores_finite", all(math.isfinite(value) for value in numeric), len(numeric))

    inventory = result["full_old26_model"]
    check(
        "analogy_inventory",
        inventory
        == {
            "training_surface_count": 1558,
            "analogy_signature_count": 1081,
            "analogy_pair_signature_count": 3493,
            "visible_condition_count": 585,
            "nullable_signature_count": 49,
        },
        inventory,
    )
    check("analogy_row_count", len(analogies) == 1081, len(analogies))
    check(
        "analogy_unique",
        len(
            {
                (
                    row["visible_insert"], row["visible_position"],
                    row["atom_insert"], row["atom_position"],
                )
                for row in analogies
            }
        )
        == len(analogies),
        len(analogies),
    )
    check(
        "pair_support_sum",
        sum(int(row["support_pair_count"]) for row in analogies) == 3493,
        sum(int(row["support_pair_count"]) for row in analogies),
    )
    probabilities = [float(row["conditional_probability"]) for row in analogies]
    check(
        "conditional_probability_range",
        min(probabilities) > 0 and max(probabilities) <= 1,
        [min(probabilities), max(probabilities)],
    )
    check("nullable_row_count", len(nullable) == 49, len(nullable))
    check(
        "nullable_exact_subset",
        nullable == [row for row in analogies if row["atom_insert"] == "NULL"],
        len(nullable),
    )
    null_map = {
        (row["visible_insert"], row["visible_position"]): int(row["support_pair_count"])
        for row in nullable
    }
    check("q_left_null", null_map[("q", "LEFT")] == 75, null_map[("q", "LEFT")])
    check("d_inner_null", null_map[("d", "INNER")] == 16, null_map[("d", "INNER")])
    check("fold_model_count", len(folds) == 4, len(folds))
    check(
        "fold_training_counts",
        [int(row["training_surface_count"]) for row in folds]
        == [1185, 1156, 1137, 1196],
        [row["training_surface_count"] for row in folds],
    )

    scopes = Counter(row["scope"] for row in ladder)
    check(
        "ladder_balanced",
        len(scopes) == 2 and len(set(scopes.values())) == 1,
        dict(scopes),
    )
    stage_scopes = Counter(row["model_stage"] for row in ladder)
    check(
        "ladder_each_stage_twice",
        all(count == 2 for count in stage_scopes.values()),
        dict(stage_scopes),
    )
    selected_rows = [row for row in ladder if row["model_stage"] == "COND_C110_W040"]
    check(
        "selected_ladder_rows",
        len(selected_rows) == 2
        and all(row["missing_relation_cost"] == "1.1" for row in selected_rows)
        and all(row["analogy_weight"] == "0.4" for row in selected_rows),
        selected_rows,
    )
    expected_surfaces = {
        row["surface"]
        for row in current
        if row["gdt522_rank"] != "1" or row["gdt521_top1"] != row["gdt522_top1"]
    }
    check(
        "candidate_truth_coverage",
        {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
        == expected_surfaces,
        len(expected_surfaces),
    )

    validation = {
        "experiment_id": "GDT522",
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
