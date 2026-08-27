#!/usr/bin/env python3
"""Independent consistency checks for GDT523 artifacts."""

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
OUT = ROOT / "experiments/yolo/gdt523_path_local_null_renderer_license/artifacts"
VALIDATION = OUT / "gdt523_validation.json"


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

    result = json.loads((OUT / "gdt523_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt523_1558_four_fold_path_null_rehearsal.tsv")
    current = read_tsv("gdt523_159_path_null_rerank.tsv")
    candidates = read_tsv("gdt523_candidate_score_atlas.tsv")
    changed = read_tsv("gdt523_changed_decision_atlas.tsv")
    remaining = read_tsv("gdt523_remaining_top1_error_atlas.tsv")
    nulls = read_tsv("gdt523_path_null_license_atlas.tsv")
    contexts = read_tsv("gdt523_left_null_atom_context_atlas.tsv")
    tradeoffs = read_tsv("gdt523_q_path_tradeoff_atlas.tsv")
    ladder = read_tsv("gdt523_model_ladder.tsv")

    check(
        "result_status",
        result["status"] == "PASS_PATH_LOCAL_DOMINANT_NULL_LICENSE",
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
        policy["stage"] == "EDIT_W025"
        and policy["feature_mode"] == "DOMINANT_EDIT"
        and policy["feature_weight"] == 0.25
        and policy["max_visible_null_insert"] == 3
        and policy["feature"] == "RELIABILITY_TIMES_VISIBLE_EDIT_WIDTH",
        policy,
    )
    check(
        "activation_gate",
        policy["activation"]
        == "PURE_LEFT_CONTIGUOUS_SURFACE_INSERTION_RELATIVE_TO_SELECTED_RENDERER_ALIAS"
        and policy["dominance_gate"]
        == "GLOBAL_AND_BASE_FIRST_ATOM_NULL_LOG_ODDS_GT_ZERO",
        [policy["activation"], policy["dominance_gate"]],
    )
    check(
        "license_inventory",
        result["license_inventory"]
        == {
            "nullable_signature_count": 49,
            "dominant_nullable_signature_count": 8,
            "left_atom_context_count": 820,
            "dominant_left_atom_context_count": 22,
        },
        result["license_inventory"],
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
    old_base = metrics(rehearsal, "gdt522_rank")
    old_selected = metrics(rehearsal, "gdt523_rank")
    check(
        "old_base_exact",
        old_base == result["old26_four_fold_gdt522_metrics"],
        old_base,
    )
    check(
        "old_selected_exact",
        old_selected == result["old26_four_fold_gdt523_metrics"],
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
            "top3_exact_count": 1387,
            "top5_exact_count": 1418,
            "rank_sum": 2111,
            "deepest_truth_rank": 22,
        },
        old_selected,
    )
    changed_old_ranks = {
        row["surface"]: (row["gdt522_rank"], row["gdt523_rank"])
        for row in rehearsal
        if row["gdt522_rank"] != row["gdt523_rank"]
    }
    check(
        "old_rank_changes",
        changed_old_ranks == {"qopchey": ("9", "8"), "qopchy": ("4", "3")},
        changed_old_ranks,
    )

    check("current_count", len(current) == 159, len(current))
    check(
        "current_surface_unique",
        len({row["surface"] for row in current}) == 159,
        len({row["surface"] for row in current}),
    )
    current_base = metrics(current, "gdt522_rank")
    current_selected = metrics(current, "gdt523_rank")
    check(
        "current_base_exact",
        current_base == result["current_gdt522_metrics"],
        current_base,
    )
    check(
        "current_selected_exact",
        current_selected == result["current_gdt523_metrics"],
        current_selected,
    )
    check(
        "current_unchanged_metrics",
        current_selected == current_base
        and current_selected["top1_exact_count"] == 142
        and current_selected["rank_sum"] == 187,
        current_selected,
    )
    classes = Counter(row["decision_change_class"] for row in current)
    check(
        "decision_classes",
        dict(sorted(classes.items())) == result["current_decision_change_classes"],
        dict(classes),
    )
    check("current_no_changed_top", not changed, len(changed))
    check("remaining_count", len(remaining) == 17, len(remaining))
    check(
        "remaining_exact",
        {row["surface"] for row in remaining}
        == {row["surface"] for row in current if row["gdt523_rank"] != "1"},
        len(remaining),
    )
    check(
        "top1_matches_top5",
        all(row["gdt523_top1"] == row["gdt523_top5"].split(" | ")[0] for row in current),
        "all rows",
    )
    check(
        "score_formula_truth",
        all(
            abs(
                float(row["truth_gdt523_score"])
                - float(row["truth_gdt522_score"])
                + 0.25 * float(row["truth_null_feature"])
            )
            < 2e-8
            for row in current
        ),
        "gdt522 - 0.25 * feature",
    )
    check(
        "score_formula_top",
        all(
            abs(
                float(row["top1_gdt523_score"])
                - float(row["top1_gdt522_score"])
                + 0.25 * float(row["top1_null_feature"])
            )
            < 2e-8
            for row in current
        ),
        "gdt522 - 0.25 * feature",
    )
    numeric = [
        float(row[field])
        for row in current
        for field in (
            "truth_gdt522_score", "truth_null_feature", "truth_gdt523_score",
            "top1_gdt522_score", "top1_null_feature", "top1_gdt523_score",
        )
    ]
    check("scores_finite", all(math.isfinite(value) for value in numeric), len(numeric))

    check("null_row_count", len(nulls) == 49, len(nulls))
    check(
        "dominant_null_count",
        sum(row["dominant_null"] == "YES" for row in nulls) == 8,
        sum(row["dominant_null"] == "YES" for row in nulls),
    )
    q_null = next(
        row for row in nulls
        if row["visible_insert"] == "q" and row["visible_position"] == "LEFT"
    )
    check(
        "q_global_null",
        q_null["null_support"] == "75"
        and q_null["competing_support"] == "9"
        and q_null["dominant_null"] == "YES",
        q_null,
    )
    check("context_row_count", len(contexts) == 820, len(contexts))
    check(
        "dominant_context_count",
        sum(row["context_dominant_null"] == "YES" for row in contexts) == 22,
        sum(row["context_dominant_null"] == "YES" for row in contexts),
    )
    context_map = {
        (row["visible_insert"], row["base_edge_atom"]): row
        for row in contexts
        if row["visible_position"] == "LEFT"
    }
    check(
        "q_atom_contexts",
        context_map[("q", "E")]["null_support"] == "1"
        and context_map[("q", "E")]["context_dominant_null"] == "YES"
        and context_map[("q", "O")]["null_support"] == "4"
        and context_map[("q", "O")]["competing_support"] == "7"
        and context_map[("q", "O")]["context_dominant_null"] == "NO"
        and context_map[("q", "OK")]["null_support"] == "33"
        and context_map[("q", "OK")]["context_dominant_null"] == "YES",
        [context_map[("q", "E")], context_map[("q", "O")], context_map[("q", "OK")]],
    )

    scopes = Counter(row["scope"] for row in ladder)
    stages = Counter(row["model_stage"] for row in ladder)
    check(
        "ladder_balanced",
        len(scopes) == 2
        and len(set(scopes.values())) == 1
        and all(count == 2 for count in stages.values()),
        {"scopes": dict(scopes), "stage_count": len(stages)},
    )
    selected_rows = [row for row in ladder if row["model_stage"] == "EDIT_W025"]
    check(
        "selected_ladder_rows",
        len(selected_rows) == 2
        and all(row["null_feature_mode"] == "DOMINANT_EDIT" for row in selected_rows)
        and all(row["null_feature_weight"] == "0.25" for row in selected_rows),
        selected_rows,
    )
    high_current = next(
        row for row in ladder
        if row["scope"] == "CURRENT_159_OLD26_TO_NEW4"
        and row["model_stage"] == "COMBINED_W085"
    )
    high_old = next(
        row for row in ladder
        if row["scope"] == "FOUR_FOLD_OLD26_SURFACE_REHEARSAL"
        and row["model_stage"] == "COMBINED_W085"
    )
    check(
        "unsafe_qef_tradeoff_metrics",
        high_current["top1_exact_count"] == "143"
        and high_old["top1_exact_count"] == "1089"
        and high_old["rank_sum"] == "2123",
        [high_current, high_old],
    )
    check(
        "tradeoff_row_count",
        len(tradeoffs) == 4 * len(stages),
        [len(tradeoffs), len(stages)],
    )
    qef_safe = next(
        row for row in tradeoffs
        if row["surface"] == "qef" and row["model_stage"] == "EDIT_W025"
    )
    qef_high = next(
        row for row in tradeoffs
        if row["surface"] == "qef" and row["model_stage"] == "COMBINED_W085"
    )
    check(
        "qef_explicit_tradeoff",
        qef_safe["truth_rank"] == "2"
        and qef_safe["top1_recipe"] == "CARRIER_Q+E+LOCAL_CHAR_F"
        and qef_high["truth_rank"] == "1"
        and qef_high["top1_recipe"] == "E+LOCAL_CHAR_F",
        [qef_safe, qef_high],
    )
    expected_surfaces = {
        row["surface"]
        for row in current
        if row["gdt523_rank"] != "1" or row["gdt522_top1"] != row["gdt523_top1"]
    }
    check(
        "candidate_truth_coverage",
        {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
        == expected_surfaces,
        len(expected_surfaces),
    )

    validation = {
        "experiment_id": "GDT523",
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
