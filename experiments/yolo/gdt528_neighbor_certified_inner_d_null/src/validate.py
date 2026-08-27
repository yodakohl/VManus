#!/usr/bin/env python3
"""Validate GDT528's action-neighbour-certified terminal-d null variant."""

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
BASE = ROOT / "experiments/yolo/gdt528_neighbor_certified_inner_d_null"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt528_validation.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    result = json.loads((OUT / "gdt528_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt528_1558_four_fold_d_null_rehearsal.tsv")
    current = read_tsv("gdt528_159_d_null_rerank.tsv")
    candidates = read_tsv("gdt528_candidate_score_atlas.tsv")
    routes = read_tsv("gdt528_d_null_route_atlas.tsv")
    pairs = read_tsv("gdt528_old_exact_d_null_pair_atlas.tsv")
    audit = read_tsv("gdt528_current_d_route_audit.tsv")
    changed = read_tsv("gdt528_changed_decision_atlas.tsv")
    ladder = read_tsv("gdt528_model_ladder.tsv")
    remaining = read_tsv("gdt528_revised_remaining_top1_error_atlas.tsv")
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check("result_status", result["status"] == "PASS_NEIGHBOR_CERTIFIED_TERMINAL_D_NULL", result["status"])
    check(
        "claim_ceiling",
        result["claim_ceiling"] == "EXPLORATORY_NEIGHBOR_CERTIFIED_TERMINAL_D_NULL_VARIANT__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        result["claim_ceiling"],
    )
    policy = result["selected_policy"]
    check(
        "selected_policy",
        policy["stage"] == "TAIL_DNULL_LOG_W115"
        and policy["feature"] == "TAIL_DNULL_LOG"
        and policy["weight"] == 1.15
        and policy["visible_frame"] == "BASE_ENDING_Y_TO_VARIANT_ENDING_DY"
        and policy["recipe_relation"] == "EXACT_EQUAL_RECIPE"
        and "ONE_KNOWN_ACTION_ROOT" in policy["recipe_neighbor"],
        policy,
    )
    naive = result["rejected_naive_visible_neighbor"]
    check(
        "naive_visible_neighbor_rejected",
        naive["stage"] == "NAIVE_TAIL_DNULL_LOG_W115"
        and naive["old26_metrics"]["top1_exact_count"] == 1098
        and naive["old26_metrics"]["top2_exact_count"] == 1327
        and naive["old26_metrics"]["rank_sum"] == 2110
        and naive["current_metrics"]["top1_exact_count"] == 149,
        naive,
    )
    check("rehearsal_count", len(rehearsal) == 1558, len(rehearsal))
    check("rehearsal_unique", len({row["surface"] for row in rehearsal}) == 1558, len({row["surface"] for row in rehearsal}))
    fold_counts = Counter(row["fold"] for row in rehearsal)
    check("fold_counts", fold_counts == Counter({"0": 373, "1": 402, "2": 421, "3": 362}), dict(fold_counts))

    expected_old = {
        "target_count": 1558, "truth_generated_count": 1441,
        "top1_exact_count": 1098, "top2_exact_count": 1328,
        "top3_exact_count": 1386, "top5_exact_count": 1418,
        "rank_sum": 2109, "deepest_truth_rank": 22,
    }
    check("old_gdt527_exact", result["old26_four_fold_gdt527_metrics"] == expected_old, result["old26_four_fold_gdt527_metrics"])
    check("old_gdt528_exact", result["old26_four_fold_gdt528_metrics"] == expected_old, result["old26_four_fold_gdt528_metrics"])
    check(
        "every_generated_old_rank_preserved",
        all(
            row["gdt527_rank"] == row["gdt528_rank"]
            and row["gdt527_top1"] == row["gdt528_top1"]
            for row in rehearsal
            if row["truth_generated"] == "YES"
        ),
        "all 1,441 generated rows",
    )
    check(
        "ungenerated_old_rows_stay_zero",
        all(
            row["gdt527_rank"] == "0" and row["gdt528_rank"] == "0"
            for row in rehearsal
            if row["truth_generated"] == "NO"
        ),
        "all 117 ungenerated rows",
    )
    check("current_count", len(current) == 159, len(current))

    expected_inherited_base = {
        "target_count": 159, "truth_generated_count": 159,
        "top1_exact_count": 148, "top2_exact_count": 156,
        "top3_exact_count": 158, "top5_exact_count": 158,
        "rank_sum": 179, "deepest_truth_rank": 9,
    }
    expected_inherited_new = {
        "target_count": 159, "truth_generated_count": 159,
        "top1_exact_count": 149, "top2_exact_count": 157,
        "top3_exact_count": 158, "top5_exact_count": 158,
        "rank_sum": 177, "deepest_truth_rank": 9,
    }
    expected_revised_base = {
        "target_count": 159, "truth_generated_count": 159,
        "top1_exact_count": 150, "top2_exact_count": 156,
        "top3_exact_count": 158, "top5_exact_count": 158,
        "rank_sum": 177, "deepest_truth_rank": 9,
    }
    expected_revised_new = {
        "target_count": 159, "truth_generated_count": 159,
        "top1_exact_count": 151, "top2_exact_count": 157,
        "top3_exact_count": 158, "top5_exact_count": 158,
        "rank_sum": 175, "deepest_truth_rank": 9,
    }
    for name, key, expected in (
        ("inherited_base", "current_inherited_gdt527_metrics", expected_inherited_base),
        ("inherited_selected", "current_inherited_gdt528_metrics", expected_inherited_new),
        ("revised_base", "current_revised_gdt527_metrics", expected_revised_base),
        ("revised_selected", "current_revised_gdt528_metrics", expected_revised_new),
    ):
        check(name, result[key] == expected, result[key])

    transitions = Counter(row["decision_change_class"] for row in current)
    expected_transitions = Counter({
        "GDT527_CORRECT_PRESERVED": 148,
        "GDT527_ERROR_CORRECTED": 1,
        "GDT527_ERROR_UNCHANGED": 10,
    })
    check("decision_transitions", transitions == expected_transitions, dict(transitions))
    check("no_current_loss", transitions["GDT527_CORRECT_LOST"] == 0, dict(transitions))
    check(
        "changed_surface",
        len(changed) == 1 and changed[0]["surface"] == "qocthedy" and result["changed_surfaces"] == ["qocthedy"],
        [row["surface"] for row in changed],
    )
    qoc = changed[0]
    check(
        "qocthedy_recipe_and_ranks",
        qoc["truth_recipe"] == "CARRIER_Q+O+CH+T+E+Y"
        and qoc["gdt527_rank"] == "3"
        and qoc["gdt527_top1"] == "CARRIER_Q+O+CH+T+E+DY"
        and qoc["gdt528_rank"] == "1"
        and qoc["gdt528_top1"] == "CARRIER_Q+O+CH+T+E+Y",
        qoc,
    )
    check(
        "score_formula",
        all(
            math.isclose(
                float(row["gdt528_score"]),
                float(row["gdt527_score"]) - 1.15 * float(row["null_feature"]),
                abs_tol=2e-8,
            )
            for row in candidates
        ),
        "gdt528 = gdt527 - 1.15*feature",
    )
    check(
        "single_selected_route",
        len(routes) == 1 and result["current_selected_route_count"] == 1 and routes[0]["surface"] == "qocthedy",
        routes,
    )
    route = routes[0]
    check(
        "exact_route",
        route["candidate_is_truth"] == "YES"
        and route["base_surface"] == "qocthey"
        and route["base_recipe"] == "CARRIER_Q+O+CH+T+E+Y"
        and route["certificate_bases"] == "qockhey"
        and route["certificate_variants"] == "qockhedy"
        and route["certificate_recipes"] == "O+CH+K+E+Y"
        and route["certificate_action_changes"] == "T>K",
        route,
    )
    check(
        "route_support_and_feature",
        route["pair_support"] == "9"
        and route["certificate_count"] == "1"
        and math.isclose(float(route["feature"]), math.log(10), abs_tol=1e-12),
        route,
    )
    terminal_count = sum(row["terminal_before_y"] == "YES" for row in pairs)
    check(
        "pair_counts",
        len(pairs) == 16 and terminal_count == 9
        and result["old_exact_inner_d_null_pair_count"] == 16
        and result["old_exact_terminal_d_null_pair_count"] == 9,
        {"all": len(pairs), "terminal": terminal_count},
    )
    expected_terminal = {
        ("chaly", "chaldy"), ("chcphy", "chcphdy"),
        ("chealy", "chealdy"), ("cheoy", "cheody"),
        ("choly", "choldy"), ("ey", "edy"),
        ("opshey", "opshedy"), ("qockhey", "qockhedy"),
        ("qokaly", "qokaldy"),
    }
    check(
        "terminal_pair_inventory",
        {(row["base_surface"], row["variant_surface"]) for row in pairs if row["terminal_before_y"] == "YES"} == expected_terminal,
        sorted(expected_terminal),
    )
    audit_by = {row["surface"]: row for row in audit}
    check("current_d_audit_scope", set(audit_by) == {"chckhedy", "cthdy", "qocthedy", "shddy"}, sorted(audit_by))
    check(
        "only_qocthedy_eligible",
        {surface for surface, row in audit_by.items() if row["selected_eligible"] == "YES"} == {"qocthedy"},
        {surface: row["selected_eligible"] for surface, row in audit_by.items()},
    )
    check(
        "counterexamples_keep_d_meaning",
        all(audit_by[surface]["truth_equals_base"] == "NO" and audit_by[surface]["selected_eligible"] == "NO" for surface in ("chckhedy", "cthdy", "shddy")),
        {surface: audit_by[surface] for surface in ("chckhedy", "cthdy", "shddy")},
    )
    ladder_by = {(row["scope"], row["model_stage"]): row for row in ladder}
    selected_old = ladder_by[("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", "TAIL_DNULL_LOG_W115")]
    check(
        "selected_ladder_row",
        selected_old["top1_exact_count"] == "1098"
        and selected_old["top2_exact_count"] == "1328"
        and selected_old["rank_sum"] == "2109",
        selected_old,
    )
    expected_remaining = {
        "aiicthy", "chekchy", "cthom", "dairykodas",
        "dalcheeeky", "dsholdaiir", "qef", "saiis",
    }
    check(
        "remaining_eight",
        len(remaining) == 8
        and result["revised_remaining_top1_error_count"] == 8
        and {row["surface"] for row in remaining} == expected_remaining,
        sorted(row["surface"] for row in remaining),
    )
    check("resolved_removed_from_queue", "qocthedy" not in {row["surface"] for row in remaining}, sorted(row["surface"] for row in remaining))
    expected_candidate_surfaces = {
        row["surface"] for row in current
        if row["gdt528_rank"] != "1" or row["gdt527_top1"] != row["gdt528_top1"]
    }
    check(
        "candidate_truth_coverage",
        {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"} == expected_candidate_surfaces,
        sorted(expected_candidate_surfaces),
    )

    validation = {
        "experiment_id": "GDT528",
        "status": "PASS" if all(row["pass"] for row in checks) else "FAIL",
        "check_count": len(checks),
        "failed_check_count": sum(not row["pass"] for row in checks),
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
