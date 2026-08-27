#!/usr/bin/env python3
"""Validate GDT527's certified terminal-s stem rule and OL revision."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt527_right_edge_learned_stem_extension"
OUT = BASE / "artifacts"
RESULT = OUT / "gdt527_result.json"
VALIDATION = OUT / "gdt527_validation.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt527_1558_four_fold_right_stem_rehearsal.tsv")
    current = read_tsv("gdt527_159_right_stem_rerank.tsv")
    candidates = read_tsv("gdt527_candidate_score_atlas.tsv")
    routes = read_tsv("gdt527_right_stem_route_atlas.tsv")
    changed = read_tsv("gdt527_changed_decision_atlas.tsv")
    ladder = read_tsv("gdt527_model_ladder.tsv")
    revisions = read_tsv("gdt527_working_revision_atlas.tsv")
    ol_rows = read_tsv("gdt527_old_ol_terminal_census.tsv")
    remaining = read_tsv("gdt527_revised_remaining_top1_error_atlas.tsv")
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_CERTIFIED_S_STEM_AND_ATOMIC_OL_REVISION",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_CERTIFIED_STEM_EXTENSION_AND_WORKING_OL_REVISION__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        result["claim_ceiling"],
    )
    policy = result["selected_policy"]
    check(
        "selected_policy",
        policy["stage"] == "CERT_S_BP1_W050"
        and policy["feature"] == "CERT_S_BP1"
        and policy["weight"] == 0.5
        and policy["suffix"] == "s->S",
        policy,
    )
    check("rehearsal_count", len(rehearsal) == 1558, len(rehearsal))
    check(
        "rehearsal_unique",
        len({row["surface"] for row in rehearsal}) == 1558,
        len({row["surface"] for row in rehearsal}),
    )
    fold_counts = Counter(row["fold"] for row in rehearsal)
    check(
        "fold_counts",
        fold_counts == Counter({"0": 373, "1": 402, "2": 421, "3": 362}),
        dict(fold_counts),
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
    check(
        "old_base_exact",
        result["old26_four_fold_gdt526_metrics"] == expected_old,
        result["old26_four_fold_gdt526_metrics"],
    )
    check(
        "old_selected_exact",
        result["old26_four_fold_gdt527_metrics"] == expected_old,
        result["old26_four_fold_gdt527_metrics"],
    )
    check("current_count", len(current) == 159, len(current))
    expected_inherited_base = {
        "target_count": 159, "truth_generated_count": 159,
        "top1_exact_count": 147, "top2_exact_count": 155,
        "top3_exact_count": 158, "top5_exact_count": 158,
        "rank_sum": 181, "deepest_truth_rank": 9,
    }
    expected_inherited_new = {
        "target_count": 159, "truth_generated_count": 159,
        "top1_exact_count": 148, "top2_exact_count": 156,
        "top3_exact_count": 158, "top5_exact_count": 158,
        "rank_sum": 179, "deepest_truth_rank": 9,
    }
    expected_revised_base = {
        "target_count": 159, "truth_generated_count": 159,
        "top1_exact_count": 149, "top2_exact_count": 155,
        "top3_exact_count": 158, "top5_exact_count": 158,
        "rank_sum": 179, "deepest_truth_rank": 9,
    }
    expected_revised_new = {
        "target_count": 159, "truth_generated_count": 159,
        "top1_exact_count": 150, "top2_exact_count": 156,
        "top3_exact_count": 158, "top5_exact_count": 158,
        "rank_sum": 177, "deepest_truth_rank": 9,
    }
    for name, key, expected in (
        ("inherited_base", "current_inherited_gdt526_metrics", expected_inherited_base),
        ("inherited_selected", "current_inherited_gdt527_metrics", expected_inherited_new),
        ("revised_base", "current_revised_gdt526_metrics", expected_revised_base),
        ("revised_selected", "current_revised_gdt527_metrics", expected_revised_new),
    ):
        check(name, result[key] == expected, result[key])

    change_counts = Counter(row["decision_change_class"] for row in current)
    expected_changes = Counter(
        {
            "GDT526_CORRECT_PRESERVED": 147,
            "GDT526_ERROR_CORRECTED": 1,
            "GDT526_ERROR_UNCHANGED": 11,
        }
    )
    check("decision_transitions", change_counts == expected_changes, dict(change_counts))
    check(
        "changed_surface",
        len(changed) == 1 and changed[0]["surface"] == "okedals",
        [row["surface"] for row in changed],
    )
    check(
        "no_current_loss",
        change_counts["GDT526_CORRECT_LOST"] == 0,
        dict(change_counts),
    )
    okedals = changed[0]
    check(
        "okedals_recipe_and_ranks",
        okedals["truth_recipe"] == "OK+AL+S"
        and okedals["gdt526_top1"] == "OK+E+D_ADDR+AL+S"
        and okedals["gdt526_rank"] == "3"
        and okedals["gdt527_top1"] == "OK+AL+S"
        and okedals["gdt527_rank"] == "1",
        okedals,
    )
    check(
        "score_formula",
        all(
            abs(
                float(row["gdt527_score"])
                - (
                    float(row["gdt526_score"])
                    - 0.5 * float(row["stem_feature"])
                )
            ) < 2e-9
            for row in candidates
        ),
        "gdt527 = gdt526 - 0.5*feature",
    )
    route_by_surface = {row["surface"]: row for row in routes}
    check(
        "route_surfaces",
        set(route_by_surface) == {"okedals", "rals"},
        sorted(route_by_surface),
    )
    ok_route = route_by_surface["okedals"]
    check(
        "okedals_exact_route",
        ok_route["candidate_recipe"] == "OK+AL+S"
        and ok_route["candidate_is_truth"] == "YES"
        and ok_route["base_surface"] == "okedal"
        and ok_route["base_recipe"] == "OK+AL"
        and ok_route["suffix"] == "s"
        and ok_route["atom_insert"] == "S"
        and ok_route["support"] == "20"
        and ok_route["total"] == "23"
        and ok_route["recipe_carrier_count"] == "5"
        and ok_route["certificate"] == "MULTI_RECIPE_CARRIERS",
        ok_route,
    )
    check(
        "okedal_recipe_carriers",
        set(ok_route["recipe_carriers"].split(" | "))
        == {"chokal", "chykald", "okal", "okedal", "qokal"},
        ok_route["recipe_carriers"],
    )
    rals = route_by_surface["rals"]
    check(
        "rals_preserved_sibling_certificate",
        rals["gdt526_rank"] == "1"
        and rals["gdt527_rank"] == "1"
        and rals["certificate"] == "ONE_CHAR_NON_NULL_RIGHT_CHILD"
        and rals["right_children"] == "raly:y->Y",
        rals,
    )
    check(
        "one_working_revision",
        len(revisions) == 1
        and revisions[0]["surface"] == "keeol"
        and revisions[0]["inherited_recipe"] == "K+EE+O+L"
        and revisions[0]["revised_recipe"] == "K+EE+OL"
        and revisions[0]["gdt526_top1"] == "K+EE+OL",
        revisions,
    )
    ol_counts = Counter(row["terminal_class"] for row in ol_rows)
    check(
        "ol_census",
        len(ol_rows) == 112
        and ol_counts == Counter({"ATOMIC_OL": 103, "O_PLUS_L": 6, "OTHER": 3}),
        dict(ol_counts),
    )
    ol_by_surface = {row["surface"]: row["terminal_class"] for row in ol_rows}
    check(
        "ol_counterexamples",
        all(
            ol_by_surface[surface] == "ATOMIC_OL"
            for surface in ("alol", "cphol", "okeol", "qokeeol", "shol")
        )
        and ol_by_surface["cheol"] == "O_PLUS_L",
        {surface: ol_by_surface[surface] for surface in (
            "alol", "cphol", "okeol", "qokeeol", "shol", "cheol"
        )},
    )
    ladder_by = {(row["scope"], row["model_stage"]): row for row in ladder}
    selected_old = ladder_by[
        ("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", "CERT_S_BP1_W050")
    ]
    rejected_l = ladder_by[
        ("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", "CERT_L_BP1_W250")
    ]
    check(
        "selected_ladder_row",
        selected_old["top1_exact_count"] == "1098"
        and selected_old["rank_sum"] == "2109",
        selected_old,
    )
    check(
        "high_l_rejected",
        rejected_l["top1_exact_count"] == "1093"
        and rejected_l["rank_sum"] == "2114",
        rejected_l,
    )
    expected_remaining = {
        "aiicthy", "chekchy", "cthom", "dairykodas", "dalcheeeky",
        "dsholdaiir", "qef", "qocthedy", "saiis",
    }
    check(
        "remaining_nine",
        len(remaining) == 9
        and {row["surface"] for row in remaining} == expected_remaining,
        sorted(row["surface"] for row in remaining),
    )
    check(
        "resolved_removed_from_queue",
        not {"keeol", "okedals"} & {row["surface"] for row in remaining},
        sorted(row["surface"] for row in remaining),
    )
    expected_candidate_surfaces = {
        row["surface"]
        for row in current
        if row["gdt527_rank"] != "1"
        or row["gdt526_top1"] != row["gdt527_top1"]
    }
    check(
        "candidate_truth_coverage",
        {
            row["surface"]
            for row in candidates
            if row["candidate_is_truth"] == "YES"
        }
        == expected_candidate_surfaces,
        len(expected_candidate_surfaces),
    )

    validation = {
        "experiment_id": "GDT527",
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
