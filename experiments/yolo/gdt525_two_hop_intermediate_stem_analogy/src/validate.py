#!/usr/bin/env python3
"""Validate GDT525's selected two-hop K-stem edition."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt525_two_hop_intermediate_stem_analogy"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt525_validation.json"


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
    result = json.loads((OUT / "gdt525_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt525_1558_four_fold_two_hop_rehearsal.tsv")
    current = read_tsv("gdt525_159_two_hop_rerank.tsv")
    candidates = read_tsv("gdt525_candidate_score_atlas.tsv")
    routes = read_tsv("gdt525_two_hop_route_atlas.tsv")
    ladder = read_tsv("gdt525_model_ladder.tsv")
    changed = read_tsv("gdt525_changed_decision_atlas.tsv")
    remaining = read_tsv("gdt525_remaining_top1_error_atlas.tsv")
    revised_remaining = read_tsv("gdt525_revised_remaining_top1_error_atlas.tsv")
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_K_BASE_Y_THEN_E_STEM_CLOSURE",
        result["status"],
    )
    check(
        "claim_ceiling_exploratory",
        result["claim_ceiling"]
        == "EXPLORATORY_TWO_HOP_LOCAL_EDIT_COMPOSITION__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        result["claim_ceiling"],
    )
    policy = result["selected_policy"]
    check(
        "selected_policy",
        policy
        == {
            "stage": "KYE_W100",
            "feature": "K_BASE_Y_THEN_E",
            "weight": 1.0,
            "route": "OLD_BASE_TO_EXPLICIT_INTERMEDIATE_TO_TARGET",
            "activation": "K_INITIAL_BASE_RECIPE__RIGHT_Y_TO_Y__THEN_INNER_E_TO_E__ORDERED_PAIR_SUPPORT_AT_LEAST_TWO",
        },
        policy,
    )
    check(
        "ordered_pair_inventory",
        result["old_ordered_pair_inventory"]
        == {
            "ordered_pair_type_count": 4833,
            "ordered_pair_carrier_count": 6141,
            "repeated_ordered_pair_type_count": 749,
        },
        result["old_ordered_pair_inventory"],
    )
    check("rehearsal_count", len(rehearsal) == 1558, len(rehearsal))
    check(
        "rehearsal_surface_unique",
        len({row["surface"] for row in rehearsal}) == 1558,
        len({row["surface"] for row in rehearsal}),
    )
    check(
        "fold_counts",
        Counter(row["fold"] for row in rehearsal)
        == Counter({"0": 373, "1": 402, "2": 421, "3": 362}),
        dict(Counter(row["fold"] for row in rehearsal)),
    )
    old_base = rank_metrics(rehearsal, "gdt524_rank")
    old_selected = rank_metrics(rehearsal, "gdt525_rank")
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
    check("old_base_exact", old_base == expected_old, old_base)
    check("old_selected_exact", old_selected == expected_old, old_selected)
    check(
        "old_result_metrics",
        result["old26_four_fold_gdt524_metrics"] == expected_old
        and result["old26_four_fold_gdt525_metrics"] == expected_old,
        [result["old26_four_fold_gdt524_metrics"], result["old26_four_fold_gdt525_metrics"]],
    )
    check("current_count", len(current) == 159, len(current))
    check(
        "current_surface_unique",
        len({row["surface"] for row in current}) == 159,
        len({row["surface"] for row in current}),
    )
    current_base = rank_metrics(current, "gdt524_rank")
    current_selected = rank_metrics(current, "gdt525_rank")
    revised_base = rank_metrics(current, "gdt524_revised_rank")
    revised_selected = rank_metrics(current, "gdt525_revised_rank")
    expected_current_base = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 144,
        "top2_exact_count": 154,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 185,
        "deepest_truth_rank": 9,
    }
    expected_current_selected = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 145,
        "top2_exact_count": 154,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 184,
        "deepest_truth_rank": 9,
    }
    expected_revised_base = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 143,
        "top2_exact_count": 153,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 187,
        "deepest_truth_rank": 9,
    }
    expected_revised_selected = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 146,
        "top2_exact_count": 154,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 183,
        "deepest_truth_rank": 9,
    }
    check("current_base_exact", current_base == expected_current_base, current_base)
    check(
        "current_selected_exact",
        current_selected == expected_current_selected,
        current_selected,
    )
    check("revised_base_exact", revised_base == expected_revised_base, revised_base)
    check(
        "revised_selected_exact",
        revised_selected == expected_revised_selected,
        revised_selected,
    )
    check(
        "result_current_metrics",
        result["current_gdt524_metrics"] == expected_current_base
        and result["current_gdt525_metrics"] == expected_current_selected
        and result["current_family_revised_gdt524_metrics"] == expected_revised_base
        and result["current_family_revised_gdt525_metrics"] == expected_revised_selected,
        "four current metric blocks",
    )
    transitions = Counter(row["decision_change_class"] for row in current)
    expected_transitions = Counter(
        {
            "GDT524_CORRECT_PRESERVED": 143,
            "GDT524_ERROR_CORRECTED": 2,
            "GDT524_CORRECT_LOST": 1,
            "GDT524_ERROR_UNCHANGED": 13,
        }
    )
    check("decision_transitions", transitions == expected_transitions, dict(transitions))
    check(
        "changed_surfaces",
        {row["surface"] for row in changed} == {"kcheody", "kechody", "keody"},
        sorted(row["surface"] for row in changed),
    )
    expected_top = {
        "kcheody": "K+CH+E+O+D_ADDR+Y",
        "kechody": "K+E+CH+O+D_ADDR+Y",
        "keody": "K+E+O+D_ADDR+Y",
    }
    observed_top = {row["surface"]: row["gdt525_top1"] for row in changed}
    check("three_k_family_tops", observed_top == expected_top, observed_top)
    revisions = {
        row["surface"]: row["revised_working_recipe"]
        for row in current
        if row["working_revision_class"] == "K_BASE_STEM_CLOSURE_REVISED"
    }
    check(
        "single_explicit_working_revision",
        revisions == {"kcheody": "K+CH+E+O+D_ADDR+Y"}
        and result["working_revisions"] == revisions,
        revisions,
    )
    check("remaining_inherited_count", len(remaining) == 14, len(remaining))
    check(
        "remaining_revised_count",
        len(revised_remaining) == 13
        and "kcheody" not in {row["surface"] for row in revised_remaining},
        len(revised_remaining),
    )
    check(
        "remaining_result_counts",
        result["remaining_top1_error_count"] == 14
        and result["revised_remaining_top1_error_count"] == 13,
        [result["remaining_top1_error_count"], result["revised_remaining_top1_error_count"]],
    )
    check(
        "score_formula",
        all(
            math.isclose(
                float(row["top1_gdt525_score"]),
                float(row["top1_gdt524_score"]) - float(row["top1_chain_feature"]),
                abs_tol=2e-8,
            )
            and math.isclose(
                float(row["truth_gdt525_score"]),
                float(row["truth_gdt524_score"]) - float(row["truth_chain_feature"]),
                abs_tol=2e-8,
            )
            for row in current
        ),
        "gdt525 = gdt524 - selected feature",
    )
    route_pairs = defaultdict(list)
    for row in routes:
        route_pairs[(row["surface"], row["candidate_recipe"])].append(row)
    check(
        "route_cardinality",
        len(routes) == 8
        and len(route_pairs) == 4
        and all(len(rows) == 2 for rows in route_pairs.values()),
        [len(routes), len(route_pairs), sorted(len(rows) for rows in route_pairs.values())],
    )
    check(
        "route_surface_scope",
        {row["surface"] for row in routes} == {"kcheody", "kechody", "keody"},
        sorted({row["surface"] for row in routes}),
    )
    check(
        "route_result_counts",
        result["current_route_candidate_count"] == 4
        and result["current_route_step_count"] == 8
        and result["current_route_surface_count"] == 3,
        [
            result["current_route_candidate_count"],
            result["current_route_step_count"],
            result["current_route_surface_count"],
        ],
    )
    for key in sorted(route_pairs):
        rows = sorted(route_pairs[key], key=lambda row: int(row["step_index"]))
        signature = [
            (
                row["visible_insert"],
                row["visible_position"],
                row["atom_insert"],
                row["atom_position"],
            )
            for row in rows
        ]
        check(
            f"route_signature_{key[0]}_{key[1]}",
            rows[0]["base_recipe"].split("+")[0] == "K"
            and signature
            == [("y", "RIGHT", "Y", "RIGHT"), ("e", "INNER", "E", "INNER")]
            and {row["ordered_pair_support"] for row in rows} == {"6"},
            {"base": rows[0]["base_surface"], "signature": signature},
        )
    ladder_by = {(row["scope"], row["model_stage"]): row for row in ladder}
    selected_rows = [
        ladder_by[("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", "KYE_W100")],
        ladder_by[("CURRENT_159_OLD26_TO_NEW4", "KYE_W100")],
    ]
    check(
        "selected_ladder_rows",
        selected_rows[0]["top1_exact_count"] == "1098"
        and selected_rows[0]["rank_sum"] == "2109"
        and selected_rows[1]["top1_exact_count"] == "145"
        and selected_rows[1]["rank_sum"] == "184",
        selected_rows,
    )
    broad_old = ladder_by[("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", "SUM_W100")]
    broad_current = ladder_by[("CURRENT_159_OLD26_TO_NEW4", "SUM_W100")]
    check(
        "broad_two_hop_rejected",
        int(broad_old["top1_exact_count"]) < 1098
        and int(broad_current["top1_exact_count"]) < 144,
        [broad_old, broad_current],
    )
    check(
        "candidate_truth_coverage",
        {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
        == {
            row["surface"]
            for row in current
            if row["gdt525_rank"] != "1" or row["gdt524_top1"] != row["gdt525_top1"]
        },
        len({row["surface"] for row in candidates}),
    )

    validation = {
        "experiment_id": "GDT525",
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
