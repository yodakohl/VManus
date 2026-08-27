#!/usr/bin/env python3
"""Independent consistency checks for GDT521 artifacts."""

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
OUT = ROOT / "experiments/yolo/gdt521_short_recipe_tail_license_reranker/artifacts"
VALIDATION = OUT / "gdt521_validation.json"


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

    result = json.loads((OUT / "gdt521_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt521_1558_four_fold_tail_rehearsal.tsv")
    current = read_tsv("gdt521_159_tail_rerank.tsv")
    candidates = read_tsv("gdt521_candidate_score_atlas.tsv")
    changed = read_tsv("gdt521_changed_decision_atlas.tsv")
    remaining = read_tsv("gdt521_remaining_top1_error_atlas.tsv")
    histories = read_tsv("gdt521_order5_history_atlas.tsv")
    families = read_tsv("gdt521_ambiguity_tail_family_atlas.tsv")
    ladder = read_tsv("gdt521_model_ladder.tsv")

    check(
        "result_status",
        result["status"] == "PASS_SHORT_RECIPE_TAIL_LICENSE_RERANKER",
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
        policy["order"] == 5
        and policy["history_atom_count"] == 4
        and policy["alpha"] == 0.5
        and policy["weight"] == 0.5,
        policy,
    )
    check(
        "training_unit",
        policy["training_unit"] == "INVARIANT_SURFACE_TYPE",
        policy["training_unit"],
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
    old_base = metrics(rehearsal, "gdt520_rank")
    old_selected = metrics(rehearsal, "gdt521_rank")
    check("old_base_exact", old_base == result["old26_four_fold_gdt520_metrics"], old_base)
    check("old_selected_exact", old_selected == result["old26_four_fold_gdt521_metrics"], old_selected)
    check("old_base_top1", old_base["top1_exact_count"] == 1089, old_base["top1_exact_count"])
    check("old_selected_top1", old_selected["top1_exact_count"] == 1090, old_selected["top1_exact_count"])
    check("old_selected_top2", old_selected["top2_exact_count"] == 1325, old_selected["top2_exact_count"])
    check("old_selected_top3", old_selected["top3_exact_count"] == 1387, old_selected["top3_exact_count"])
    check("old_selected_top5", old_selected["top5_exact_count"] == 1418, old_selected["top5_exact_count"])
    check("old_selected_rank_sum", old_selected["rank_sum"] == 2118, old_selected["rank_sum"])
    check("old_selected_deepest", old_selected["deepest_truth_rank"] == 22, old_selected["deepest_truth_rank"])

    check("current_count", len(current) == 159, len(current))
    check(
        "current_surface_unique",
        len({row["surface"] for row in current}) == 159,
        len({row["surface"] for row in current}),
    )
    current_base = metrics(current, "gdt520_rank")
    current_selected = metrics(current, "gdt521_rank")
    check("current_base_exact", current_base == result["current_gdt520_metrics"], current_base)
    check("current_selected_exact", current_selected == result["current_gdt521_metrics"], current_selected)
    check("current_base_top1", current_base["top1_exact_count"] == 139, current_base["top1_exact_count"])
    check("current_selected_top1", current_selected["top1_exact_count"] == 140, current_selected["top1_exact_count"])
    check("current_selected_top2", current_selected["top2_exact_count"] == 154, current_selected["top2_exact_count"])
    check("current_selected_top3", current_selected["top3_exact_count"] == 158, current_selected["top3_exact_count"])
    check("current_selected_top5", current_selected["top5_exact_count"] == 158, current_selected["top5_exact_count"])
    check("current_selected_rank_sum", current_selected["rank_sum"] == 189, current_selected["rank_sum"])
    check("current_selected_deepest", current_selected["deepest_truth_rank"] == 9, current_selected["deepest_truth_rank"])
    classes = Counter(row["decision_change_class"] for row in current)
    check(
        "decision_classes",
        dict(sorted(classes.items())) == result["current_decision_change_classes"],
        dict(classes),
    )
    check("corrected_count", classes["GDT520_ERROR_CORRECTED"] == 1, classes["GDT520_ERROR_CORRECTED"])
    check("lost_count", classes["GDT520_CORRECT_LOST"] == 0, classes["GDT520_CORRECT_LOST"])
    check("changed_wrong_count", classes["ERROR_CHANGED_STILL_WRONG"] == 1, classes["ERROR_CHANGED_STILL_WRONG"])
    check(
        "changed_surfaces",
        {row["surface"] for row in changed} == {"dyky", "psheody"},
        sorted(row["surface"] for row in changed),
    )
    check(
        "psheody_corrected",
        any(
            row["surface"] == "psheody"
            and row["gdt521_top1"] == "P+SH+E+O+D_ADDR+Y"
            and row["gdt521_rank"] == "1"
            for row in current
        ),
        "P+SH+E+O+D_ADDR+Y",
    )
    check("remaining_count", len(remaining) == 19, len(remaining))
    check(
        "remaining_exact",
        {row["surface"] for row in remaining}
        == {row["surface"] for row in current if row["gdt521_rank"] != "1"},
        len(remaining),
    )
    check(
        "top1_matches_top5",
        all(row["gdt521_top1"] == row["gdt521_top5"].split(" | ")[0] for row in current),
        "all rows",
    )
    check(
        "truth_top1_consistency",
        all((row["gdt521_rank"] == "1") == (row["truth_recipe"] == row["gdt521_top1"]) for row in current),
        "all rows",
    )
    check(
        "score_formula_truth",
        all(
            abs(
                float(row["truth_gdt521_score"])
                - float(row["truth_gdt520_score"])
                - 0.5 * float(row["truth_order5_nll"])
            ) < 2e-8
            for row in current
        ),
        "weight 0.5",
    )
    check(
        "score_formula_top",
        all(
            abs(
                float(row["top1_gdt521_score"])
                - float(row["top1_gdt520_score"])
                - 0.5 * float(row["top1_order5_nll"])
            ) < 2e-8
            for row in current
        ),
        "weight 0.5",
    )
    numeric = [
        float(row[field])
        for row in current
        for field in (
            "truth_gdt520_score", "truth_order5_nll", "truth_gdt521_score",
            "top1_gdt520_score", "top1_order5_nll", "top1_gdt521_score",
        )
    ]
    check("scores_finite", all(math.isfinite(value) for value in numeric), len(numeric))
    check("scores_nonnegative", min(numeric) >= 0, min(numeric))
    check(
        "alignment_traces_present",
        all("=>" in row["truth_alignment_trace"] and "~" in row["top1_alignment_trace"] for row in current),
        "all rows",
    )

    check("history_row_count", len(histories) == 3284, len(histories))
    check(
        "history_count",
        len({row["history"] for row in histories}) == 1993,
        len({row["history"] for row in histories}),
    )
    check("history_order", all(row["order"] == "5" for row in histories), "all rows")
    check("history_alpha", all(row["alpha"] == "0.5" for row in histories), "all rows")
    check("history_vocabulary", all(row["vocabulary_count"] == "44" for row in histories), "all rows")
    probabilities = [float(row["smoothed_probability"]) for row in histories]
    check(
        "history_probability_unit_interval",
        min(probabilities) > 0 and max(probabilities) < 1,
        [min(probabilities), max(probabilities)],
    )
    check("family_row_count", len(families) == 10, len(families))
    family_values = {(row["family"], row["tail_recipe"]): int(row["old_surface_type_count"]) for row in families}
    check("o_dy_types", family_values[("O_CLOSE", "O+DY")] == 30, family_values[("O_CLOSE", "O+DY")])
    check("o_dy_split_types", family_values[("O_CLOSE", "O+D_ADDR+Y")] == 17, family_values[("O_CLOSE", "O+D_ADDR+Y")])
    check("ol_types", family_values[("OL_CLOSE", "OL")] == 107, family_values[("OL_CLOSE", "OL")])
    check("o_l_types", family_values[("OL_CLOSE", "O+L")] == 6, family_values[("OL_CLOSE", "O+L")])
    check("iin_exact_old_absence", family_values[("D_IIN_R", "D_ADDR+IIN+R")] == 0, family_values[("D_IIN_R", "D_ADDR+IIN+R")])

    check("candidate_count", len(candidates) == 214, len(candidates))
    expected_surfaces = {
        row["surface"]
        for row in current
        if row["gdt521_rank"] != "1" or row["gdt520_top1"] != row["gdt521_top1"]
    }
    check(
        "candidate_truth_coverage",
        {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
        == expected_surfaces,
        len(expected_surfaces),
    )
    check("ladder_count", len(ladder) == 18, len(ladder))
    selected_old = next(
        row for row in ladder
        if row["scope"] == "FOUR_FOLD_OLD26_SURFACE_REHEARSAL"
        and row["model_stage"] == "GDT521_SELECTED"
    )
    selected_current = next(
        row for row in ladder
        if row["scope"] == "CURRENT_159_OLD26_TO_NEW4"
        and row["model_stage"] == "GDT521_SELECTED"
    )
    check(
        "ladder_selected_old",
        selected_old["top1_exact_count"] == "1090" and selected_old["rank_sum"] == "2118",
        [selected_old["top1_exact_count"], selected_old["rank_sum"]],
    )
    check(
        "ladder_selected_current",
        selected_current["top1_exact_count"] == "140" and selected_current["rank_sum"] == "189",
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
        "experiment_id": "GDT521",
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
