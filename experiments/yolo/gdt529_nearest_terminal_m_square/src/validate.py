#!/usr/bin/env python3
"""Validate GDT529's action-slot terminal-m square."""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt529_nearest_terminal_m_square"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt529_validation.json"
ALIGN = BASE / "src/align_surface.py"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    result = json.loads((OUT / "gdt529_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt529_1558_four_fold_m_square_rehearsal.tsv")
    current = read_tsv("gdt529_159_m_square_rerank.tsv")
    candidates = read_tsv("gdt529_candidate_score_atlas.tsv")
    routes = read_tsv("gdt529_m_square_route_atlas.tsv")
    pairs = read_tsv("gdt529_old_exact_terminal_m_pair_atlas.tsv")
    audit = read_tsv("gdt529_current_terminal_m_audit.tsv")
    predictions = read_tsv("gdt529_action_slot_prediction_atlas.tsv")
    changed = read_tsv("gdt529_changed_decision_atlas.tsv")
    ladder = read_tsv("gdt529_model_ladder.tsv")
    remaining = read_tsv("gdt529_revised_remaining_top1_error_atlas.tsv")
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_ACTION_SLOT_TERMINAL_M_SQUARE",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_ACTION_SLOT_TERMINAL_M_SQUARE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        result["claim_ceiling"],
    )
    policy = result["selected_policy"]
    check(
        "selected_policy",
        policy["stage"] == "DUAL_M_SQUARE_BIN_W125"
        and policy["feature"] == "DUAL_SQUARE_BINARY"
        and policy["weight"] == 1.25
        and "O_OL_OR" in policy["family_certificate"]
        and "ONE_VISIBLE_EDIT" in policy["edit_certificate"],
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
        "old_gdt528_exact",
        result["old26_four_fold_gdt528_metrics"] == expected_old,
        result["old26_four_fold_gdt528_metrics"],
    )
    check(
        "old_gdt529_exact",
        result["old26_four_fold_gdt529_metrics"] == expected_old,
        result["old26_four_fold_gdt529_metrics"],
    )
    check(
        "every_generated_old_rank_preserved",
        all(
            row["gdt528_rank"] == row["gdt529_rank"]
            and row["gdt528_top1"] == row["gdt529_top1"]
            for row in rehearsal
            if row["truth_generated"] == "YES"
        ),
        "all 1,441 generated rows",
    )
    check(
        "ungenerated_old_rows_stay_zero",
        all(
            row["gdt528_rank"] == "0" and row["gdt529_rank"] == "0"
            for row in rehearsal
            if row["truth_generated"] == "NO"
        ),
        "all 117 ungenerated rows",
    )
    check("current_count", len(current) == 159, len(current))
    expected_inherited_base = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 149,
        "top2_exact_count": 157,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 177,
        "deepest_truth_rank": 9,
    }
    expected_inherited_new = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 150,
        "top2_exact_count": 157,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 176,
        "deepest_truth_rank": 9,
    }
    expected_revised_base = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 151,
        "top2_exact_count": 157,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 175,
        "deepest_truth_rank": 9,
    }
    expected_revised_new = {
        "target_count": 159,
        "truth_generated_count": 159,
        "top1_exact_count": 152,
        "top2_exact_count": 157,
        "top3_exact_count": 158,
        "top5_exact_count": 158,
        "rank_sum": 174,
        "deepest_truth_rank": 9,
    }
    for name, key, expected in (
        ("inherited_base", "current_inherited_gdt528_metrics", expected_inherited_base),
        ("inherited_selected", "current_inherited_gdt529_metrics", expected_inherited_new),
        ("revised_base", "current_revised_gdt528_metrics", expected_revised_base),
        ("revised_selected", "current_revised_gdt529_metrics", expected_revised_new),
    ):
        check(name, result[key] == expected, result[key])
    transitions = Counter(row["decision_change_class"] for row in current)
    expected_transitions = Counter(
        {
            "GDT528_CORRECT_PRESERVED": 149,
            "GDT528_ERROR_CORRECTED": 1,
            "GDT528_ERROR_UNCHANGED": 9,
        }
    )
    check("decision_transitions", transitions == expected_transitions, dict(transitions))
    check("no_current_loss", transitions["GDT528_CORRECT_LOST"] == 0, dict(transitions))
    check(
        "changed_surface",
        len(changed) == 1
        and changed[0]["surface"] == "cthom"
        and result["changed_surfaces"] == ["cthom"],
        [row["surface"] for row in changed],
    )
    cthom = changed[0]
    check(
        "cthom_recipe_and_ranks",
        cthom["truth_recipe"] == "CH+T+O+M_LOCAL"
        and cthom["gdt528_rank"] == "2"
        and cthom["gdt528_top1"] == "CH+T+O+AM_ADDR"
        and cthom["gdt529_rank"] == "1"
        and cthom["gdt529_top1"] == "CH+T+O+M_LOCAL",
        cthom,
    )
    check(
        "score_formula",
        all(
            math.isclose(
                float(row["gdt529_score"]),
                float(row["gdt528_score"]) - 1.25 * float(row["square_feature"]),
                abs_tol=2e-8,
            )
            for row in candidates
        ),
        "gdt529 = gdt528 - 1.25*feature",
    )
    check(
        "single_selected_route",
        len(routes) == 1
        and result["current_selected_route_count"] == 1
        and routes[0]["surface"] == "cthom",
        routes,
    )
    route = routes[0]
    check(
        "exact_dual_route",
        route["candidate_is_truth"] == "YES"
        and route["base_surface"] == "ctho"
        and route["base_recipe"] == "CH+T+O"
        and route["stem_surface"] == "cth"
        and route["stem_recipe"] == "CH+T"
        and route["o_surface"] == "ctho"
        and route["ol_surface"] == "cthol"
        and route["or_surface"] == "cthor"
        and route["predicted_terminal_atom"] == "M_LOCAL",
        route,
    )
    check(
        "edit_pair_certificate",
        route["nearest_distance"] == "1"
        and route["certificate_bases"] == "cho"
        and route["certificate_variants"] == "chom"
        and route["certificate_recipes"] == "HO+M_LOCAL"
        and route["pair_inventory_size"] == "8",
        route,
    )
    expected_pairs = {
        ("cheo", "cheom", "AM_ADDR"),
        ("cho", "chom", "M_LOCAL"),
        ("lo", "lom", "M_LOCAL"),
        ("o", "om", "AM_ADDR"),
        ("okcho", "okchom", "AM_ADDR"),
        ("okeo", "okeom", "AM_ADDR"),
        ("qokeo", "qokeom", "AM_ADDR"),
        ("sheo", "sheom", "AM_ADDR"),
    }
    check(
        "terminal_m_pair_inventory",
        len(pairs) == 8
        and result["old_exact_terminal_m_pair_count"] == 8
        and {
            (row["base_surface"], row["variant_surface"], row["terminal_atom"])
            for row in pairs
        }
        == expected_pairs,
        pairs,
    )
    prediction_by = {row["stem_surface"]: row for row in predictions}
    check(
        "four_action_slot_families",
        set(prediction_by) == {"ckh", "cph", "cth", "tsh"}
        and result["old_action_slot_family_count"] == 4,
        sorted(prediction_by),
    )
    check(
        "three_licensed_predictions",
        result["licensed_action_slot_m_prediction_count"] == 3
        and {
            row["terminal_m_surface"]
            for row in predictions
            if row["decision"] == "LICENSED"
        }
        == {"ckhom", "cphom", "cthom"},
        predictions,
    )
    check(
        "tshom_unresolved",
        prediction_by["tsh"]["terminal_m_surface"] == "tshom"
        and prediction_by["tsh"]["decision"] == "NO_ONE_EDIT_PAIR_CERTIFICATE"
        and prediction_by["tsh"]["predicted_recipe"] == "UNRESOLVED",
        prediction_by["tsh"],
    )
    audit_by = {row["surface"]: row for row in audit}
    check(
        "current_terminal_m_audit_scope",
        set(audit_by) == {"cthom", "ofaram", "okedam"},
        sorted(audit_by),
    )
    check(
        "only_cthom_licensed",
        {surface for surface, row in audit_by.items() if row["truth_licensed"] == "YES"}
        == {"cthom"},
        {surface: row["truth_licensed"] for surface, row in audit_by.items()},
    )
    ladder_by = {(row["scope"], row["model_stage"]): row for row in ladder}
    selected_old = ladder_by[
        ("FOUR_FOLD_OLD26_SURFACE_REHEARSAL", "DUAL_M_SQUARE_BIN_W125")
    ]
    check(
        "selected_ladder_row",
        selected_old["top1_exact_count"] == "1098"
        and selected_old["top2_exact_count"] == "1328"
        and selected_old["rank_sum"] == "2109",
        selected_old,
    )
    expected_remaining = {
        "aiicthy",
        "chekchy",
        "dairykodas",
        "dalcheeeky",
        "dsholdaiir",
        "qef",
        "saiis",
    }
    check(
        "remaining_seven",
        len(remaining) == 7
        and result["revised_remaining_top1_error_count"] == 7
        and {row["surface"] for row in remaining} == expected_remaining,
        sorted(row["surface"] for row in remaining),
    )
    check(
        "cthom_removed_from_queue",
        "cthom" not in {row["surface"] for row in remaining},
        sorted(row["surface"] for row in remaining),
    )
    completed = subprocess.run(
        [sys.executable, str(ALIGN), "--surface", "cthom", "--top", "2"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    aligned = json.loads(completed.stdout)
    check(
        "executable_cthom_default",
        aligned["default_selection"] == "CH+T+O+M_LOCAL"
        and aligned["reranked_candidates"][0]["recipe"] == "CH+T+O+M_LOCAL"
        and aligned["reranked_candidates"][0]["m_square_certificate"] == "cho->chom",
        aligned,
    )
    check(
        "executable_guard",
        aligned["selected_stage"] == "DUAL_M_SQUARE_BIN_W125"
        and "NO_GLOBAL_M_LOCAL_DEFAULT" in aligned["guard"],
        {"stage": aligned["selected_stage"], "guard": aligned["guard"]},
    )

    validation = {
        "experiment_id": "GDT529",
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
