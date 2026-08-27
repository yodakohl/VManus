#!/usr/bin/env python3
"""Independent consistency checks for GDT524 artifacts."""

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
OUT = ROOT / "experiments/yolo/gdt524_multi_base_analogy_consensus/artifacts"
VALIDATION = OUT / "gdt524_validation.json"


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

    result = json.loads((OUT / "gdt524_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt524_1558_four_fold_multi_base_rehearsal.tsv")
    current = read_tsv("gdt524_159_multi_base_rerank.tsv")
    candidates = read_tsv("gdt524_candidate_score_atlas.tsv")
    changed = read_tsv("gdt524_changed_decision_atlas.tsv")
    remaining = read_tsv("gdt524_remaining_top1_error_atlas.tsv")
    routes = read_tsv("gdt524_multi_base_route_atlas.tsv")
    ladder = read_tsv("gdt524_model_ladder.tsv")

    check(
        "result_status",
        result["status"] == "PASS_TWO_INDEPENDENT_BASE_ANALOGY_CONSENSUS",
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
        policy["stage"] == "SUM2_W100"
        and policy["feature"] == "SUM_TWO"
        and policy["weight"] == 1.0
        and policy["aggregation"] == "SUM_OF_TWO_STRONGEST_DISTINCT_BASE_BONUSES",
        policy,
    )
    check(
        "independence_policy",
        policy["independence_unit"]
        == "DISTINCT_OLD_BASE_SURFACE_AND_DISTINCT_VISIBLE_TO_ATOM_EDIT_CHANNEL"
        and policy["activation"]
        == "AT_LEAST_TWO_POSITIVE_GDT522_LICENSE_BONUSES_WITH_DIFFERENT_NORMALIZED_CHANNELS",
        [policy["independence_unit"], policy["activation"]],
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
    old_base = metrics(rehearsal, "gdt523_rank")
    old_selected = metrics(rehearsal, "gdt524_rank")
    check(
        "old_base_exact",
        old_base == result["old26_four_fold_gdt523_metrics"],
        old_base,
    )
    check(
        "old_selected_exact",
        old_selected == result["old26_four_fold_gdt524_metrics"],
        old_selected,
    )
    check(
        "old_selected_expected",
        old_selected
        == {
            "target_count": 1558,
            "truth_generated_count": 1441,
            "top1_exact_count": 1098,
            "top2_exact_count": 1328,
            "top3_exact_count": 1386,
            "top5_exact_count": 1418,
            "rank_sum": 2109,
            "deepest_truth_rank": 22,
        },
        old_selected,
    )
    old_classes = Counter()
    for row in rehearsal:
        base_rank = int(row["gdt523_rank"])
        selected_rank = int(row["gdt524_rank"])
        if base_rank == 1 and selected_rank == 1:
            old_classes["PRESERVED"] += 1
        elif base_rank != 1 and selected_rank == 1:
            old_classes["CORRECTED"] += 1
        elif base_rank == 1 and selected_rank != 1:
            old_classes["LOST"] += 1
    check(
        "old_top1_transitions",
        old_classes["CORRECTED"] == 2 and old_classes["LOST"] == 0,
        dict(old_classes),
    )
    old_corrected = {
        row["surface"]
        for row in rehearsal
        if row["gdt523_rank"] != "1" and row["gdt524_rank"] == "1"
    }
    check(
        "old_corrected_surfaces",
        old_corrected == {"qoteody", "shkchy"},
        sorted(old_corrected),
    )

    check("current_count", len(current) == 159, len(current))
    check(
        "current_surface_unique",
        len({row["surface"] for row in current}) == 159,
        len({row["surface"] for row in current}),
    )
    current_base = metrics(current, "gdt523_rank")
    current_selected = metrics(current, "gdt524_rank")
    check(
        "current_base_exact",
        current_base == result["current_gdt523_metrics"],
        current_base,
    )
    check(
        "current_selected_exact",
        current_selected == result["current_gdt524_metrics"],
        current_selected,
    )
    check(
        "current_selected_expected",
        current_selected
        == {
            "target_count": 159,
            "truth_generated_count": 159,
            "top1_exact_count": 144,
            "top2_exact_count": 154,
            "top3_exact_count": 158,
            "top5_exact_count": 158,
            "rank_sum": 185,
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
        "current_two_corrections_no_loss",
        classes["GDT523_ERROR_CORRECTED"] == 2
        and classes["GDT523_CORRECT_LOST"] == 0,
        dict(classes),
    )
    check(
        "changed_surfaces",
        {row["surface"] for row in changed} == {"kchody", "ld"},
        sorted(row["surface"] for row in changed),
    )
    corrections = {row["surface"]: row["gdt524_top1"] for row in changed}
    check(
        "corrected_recipes",
        corrections
        == {
            "kchody": "K+CH+O+D_ADDR+Y",
            "ld": "L+D_ADDR",
        },
        corrections,
    )
    check("remaining_count", len(remaining) == 15, len(remaining))
    check(
        "remaining_exact",
        {row["surface"] for row in remaining}
        == {row["surface"] for row in current if row["gdt524_rank"] != "1"},
        len(remaining),
    )
    check(
        "top1_matches_top5",
        all(row["gdt524_top1"] == row["gdt524_top5"].split(" | ")[0] for row in current),
        "all rows",
    )
    check(
        "score_formula_truth",
        all(
            abs(
                float(row["truth_gdt524_score"])
                - float(row["truth_gdt523_score"])
                + float(row["truth_consensus_feature"])
            )
            < 2e-8
            for row in current
        ),
        "gdt523 - feature",
    )
    check(
        "score_formula_top",
        all(
            abs(
                float(row["top1_gdt524_score"])
                - float(row["top1_gdt523_score"])
                + float(row["top1_consensus_feature"])
            )
            < 2e-8
            for row in current
        ),
        "gdt523 - feature",
    )
    numeric = [
        float(row[field])
        for row in current
        for field in (
            "truth_gdt523_score", "truth_consensus_feature", "truth_gdt524_score",
            "top1_gdt523_score", "top1_consensus_feature", "top1_gdt524_score",
        )
    ]
    check("scores_finite", all(math.isfinite(value) for value in numeric), len(numeric))

    route_pairs = {
        (row["surface"], row["candidate_recipe"])
        for row in routes
    }
    check(
        "multi_base_candidate_count",
        len(route_pairs) == result["current_multi_base_candidate_count"] == 25,
        len(route_pairs),
    )
    route_counts = Counter((row["surface"], row["candidate_recipe"]) for row in routes)
    check(
        "exactly_two_selected_routes",
        len(routes) == 50 and all(count == 2 for count in route_counts.values()),
        [len(routes), sorted(set(route_counts.values()))],
    )
    for key, rows in {
        pair: [row for row in routes if (row["surface"], row["candidate_recipe"]) == pair]
        for pair in sorted(route_pairs)
    }.items():
        channels = {(row["visible_insert"], row["atom_insert"]) for row in rows}
        check(
            f"distinct_channels_{key[0]}_{key[1]}",
            len(channels) == 2 and len({row["base_surface"] for row in rows}) == 2,
            {"channels": sorted(channels), "bases": sorted(row["base_surface"] for row in rows)},
        )
    check(
        "kcheeky_same_channel_blocked",
        not any(row["surface"] == "kcheeky" for row in routes)
        and next(row for row in current if row["surface"] == "kcheeky")["gdt524_rank"] == "1",
        "no consensus route and truth preserved",
    )
    expected_routes = {
        "kchody": {
            ("kchod", "y", "Y"),
            ("chody", "k", "K"),
        },
        "ld": {
            ("d", "l", "L"),
            ("l", "d", "D_ADDR"),
        },
    }
    for surface, expected in expected_routes.items():
        observed = {
            (row["base_surface"], row["visible_insert"], row["atom_insert"])
            for row in routes
            if row["surface"] == surface and row["candidate_is_truth"] == "YES"
        }
        check(f"{surface}_route_pair", observed == expected, sorted(observed))

    scopes = Counter(row["scope"] for row in ladder)
    stages = Counter(row["model_stage"] for row in ladder)
    check(
        "ladder_balanced",
        len(scopes) == 2
        and len(set(scopes.values())) == 1
        and all(count == 2 for count in stages.values()),
        {"scopes": dict(scopes), "stage_count": len(stages)},
    )
    selected_rows = [row for row in ladder if row["model_stage"] == "SUM2_W100"]
    check(
        "selected_ladder_rows",
        len(selected_rows) == 2
        and all(row["consensus_feature"] == "SUM_TWO" for row in selected_rows)
        and all(row["consensus_weight"] == "1.0" for row in selected_rows),
        selected_rows,
    )
    expected_surfaces = {
        row["surface"]
        for row in current
        if row["gdt524_rank"] != "1" or row["gdt523_top1"] != row["gdt524_top1"]
    }
    check(
        "candidate_truth_coverage",
        {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
        == expected_surfaces,
        len(expected_surfaces),
    )

    validation = {
        "experiment_id": "GDT524",
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
