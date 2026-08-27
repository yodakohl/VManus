#!/usr/bin/env python3
"""Independent consistency checks for GDT519 artifacts."""

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
OUT = ROOT / "experiments/yolo/gdt519_visible_stem_anchor_transducer/artifacts"
VALIDATION = OUT / "gdt519_validation.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def stable_fold(surface: str) -> int:
    digest = hashlib.sha256(surface.encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % 4


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    result = json.loads((OUT / "gdt519_result.json").read_text(encoding="utf-8"))
    rehearsal = read_tsv("gdt519_1558_four_fold_surface_rehearsal.tsv")
    current = read_tsv("gdt519_159_anchor_rerank.tsv")
    lexicon = read_tsv("gdt519_anchor_alias_lexicon.tsv")
    candidates = read_tsv("gdt519_candidate_alignment_atlas.tsv")
    changed = read_tsv("gdt519_changed_decision_atlas.tsv")
    remaining = read_tsv("gdt519_remaining_top1_error_atlas.tsv")
    ladder = read_tsv("gdt519_model_ladder.tsv")

    check("result_status", result["status"] == "PASS_VISIBLE_STEM_ANCHOR_TRANSDUCER", result["status"])
    check("claim_ceiling_exploratory", result["claim_ceiling"].startswith("EXPLORATORY_"), result["claim_ceiling"])
    check("rehearsal_count", len(rehearsal) == 1558, len(rehearsal))
    check("rehearsal_surface_unique", len({row["surface"] for row in rehearsal}) == 1558, len({row["surface"] for row in rehearsal}))
    observed_folds = Counter(row["fold"] for row in rehearsal)
    check("fold_counts", observed_folds == Counter({"0": 373, "1": 402, "2": 421, "3": 362}), dict(observed_folds))
    check("fold_hash_assignment", all(int(row["fold"]) == stable_fold(row["surface"]) for row in rehearsal), "all rows")
    check("rehearsal_generated", sum(row["truth_generated"] == "YES" for row in rehearsal) == 1441, sum(row["truth_generated"] == "YES" for row in rehearsal))
    check("rehearsal_unparsed_zero_ranks", all((row["truth_generated"] == "YES") or (row["compiler_rank"] == row["form_decoder_rank"] == row["anchor_rank"] == "0") for row in rehearsal), "all rows")
    check("rehearsal_compiler_top1", sum(row["compiler_rank"] == "1" for row in rehearsal) == 1000, sum(row["compiler_rank"] == "1" for row in rehearsal))
    check("rehearsal_form_top1", sum(row["form_decoder_rank"] == "1" for row in rehearsal) == 1054, sum(row["form_decoder_rank"] == "1" for row in rehearsal))
    check("rehearsal_anchor_top1", sum(row["anchor_rank"] == "1" for row in rehearsal) == 1082, sum(row["anchor_rank"] == "1" for row in rehearsal))
    check("rehearsal_anchor_top5", sum(0 < int(row["anchor_rank"]) <= 5 for row in rehearsal) == 1418, sum(0 < int(row["anchor_rank"]) <= 5 for row in rehearsal))
    check("rehearsal_anchor_rank_sum", sum(int(row["anchor_rank"]) for row in rehearsal) == 2152, sum(int(row["anchor_rank"]) for row in rehearsal))
    check("rehearsal_anchor_deepest", max(int(row["anchor_rank"]) for row in rehearsal) == 23, max(int(row["anchor_rank"]) for row in rehearsal))

    full_lexicon = [row for row in lexicon if row["model"] == "FULL_OLD26"]
    check("full_lexicon_option_count", len(full_lexicon) == 473, len(full_lexicon))
    check("full_renderer_sequence_count", len({row["atom_sequence"] for row in full_lexicon}) == 332, len({row["atom_sequence"] for row in full_lexicon}))
    check("canonical_atom_count", sum(row["atom_count"] == "1" and row["alias_source"] in {"CANONICAL_STEM", "CANONICAL_AND_LEARNED"} for row in full_lexicon) == 45, sum(row["atom_count"] == "1" and row["alias_source"] in {"CANONICAL_STEM", "CANONICAL_AND_LEARNED"} for row in full_lexicon))
    check("renderer_width_bounded", all(1 <= int(row["atom_count"]) <= 3 for row in lexicon), "all rows")
    learned = [row for row in lexicon if row["alias_source"].startswith("LEARNED")]
    check("learned_support_floor", min(int(row["support"]) for row in learned) >= 10, min(int(row["support"]) for row in learned))
    check("single_share_floor", all(float(row["support_share"]) >= 0.70 for row in learned if row["atom_count"] == "1"), "single aliases")
    check("multi_share_floor", all(float(row["support_share"]) >= 0.60 for row in learned if row["atom_count"] != "1"), "multi aliases")
    check("alias_penalties_nonnegative", all(float(row["alias_penalty"]) >= 0 for row in lexicon), min(float(row["alias_penalty"]) for row in lexicon))
    check("chek_renderer_present", any(row["model"] == "FULL_OLD26" and row["atom_sequence"] == "CH+K" and row["surface_alias"] == "chek" for row in lexicon), "CH+K <- chek")

    check("current_count", len(current) == 159, len(current))
    check("current_surface_unique", len({row["surface"] for row in current}) == 159, len({row["surface"] for row in current}))
    check("current_all_generated", all(int(row["gdt519_rank"]) > 0 for row in current), "159 rows")
    check("gdt518_top1", sum(row["gdt518_rank"] == "1" for row in current) == 134, sum(row["gdt518_rank"] == "1" for row in current))
    check("gdt519_top1", sum(row["gdt519_rank"] == "1" for row in current) == 138, sum(row["gdt519_rank"] == "1" for row in current))
    check("gdt519_top2", sum(int(row["gdt519_rank"]) <= 2 for row in current) == 153, sum(int(row["gdt519_rank"]) <= 2 for row in current))
    check("gdt519_top3", sum(int(row["gdt519_rank"]) <= 3 for row in current) == 157, sum(int(row["gdt519_rank"]) <= 3 for row in current))
    check("gdt519_top5", sum(int(row["gdt519_rank"]) <= 5 for row in current) == 158, sum(int(row["gdt519_rank"]) <= 5 for row in current))
    check("gdt519_rank_sum", sum(int(row["gdt519_rank"]) for row in current) == 192, sum(int(row["gdt519_rank"]) for row in current))
    check("gdt519_deepest", max(int(row["gdt519_rank"]) for row in current) == 8, max(int(row["gdt519_rank"]) for row in current))
    classes = Counter(row["decision_change_class"] for row in current)
    check("decision_classes_match", dict(sorted(classes.items())) == result["current_decision_change_classes"], dict(classes))
    check("corrected_count", classes["GDT518_ERROR_CORRECTED"] == 8, classes["GDT518_ERROR_CORRECTED"])
    check("lost_count", classes["GDT518_CORRECT_LOST"] == 4, classes["GDT518_CORRECT_LOST"])
    check("changed_count", len(changed) == 13, len(changed))
    check("remaining_count", len(remaining) == 21, len(remaining))
    check("changed_rows_exact", {row["surface"] for row in changed} == {row["surface"] for row in current if row["gdt518_top1"] != row["gdt519_top1"]}, len(changed))
    check("remaining_rows_exact", {row["surface"] for row in remaining} == {row["surface"] for row in current if row["gdt519_rank"] != "1"}, len(remaining))
    check("top1_matches_top5", all(row["gdt519_top1"] == row["gdt519_top5"].split(" | ")[0] for row in current), "all rows")
    check("truth_top1_consistency", all((row["gdt519_rank"] == "1") == (row["truth_recipe"] == row["gdt519_top1"]) for row in current), "all rows")
    check("alignment_traces_present", all("=>" in row["truth_alignment_trace"] and "~" in row["top1_alignment_trace"] for row in current), "all rows")
    check("selected_score_formula_truth", all(abs(float(row["truth_selected_score"]) - float(row["truth_base_score"]) - float(row["truth_anchor_cost"])) < 2e-8 for row in current), "weight 1")
    check("selected_score_formula_top", all(abs(float(row["top1_selected_score"]) - float(row["top1_base_score"]) - float(row["top1_anchor_cost"])) < 2e-8 for row in current), "weight 1")
    numeric = [float(row[field]) for row in current for field in ("truth_base_score", "truth_anchor_cost", "truth_selected_score", "top1_base_score", "top1_anchor_cost", "top1_selected_score")]
    check("scores_finite", all(math.isfinite(value) for value in numeric), len(numeric))
    check("scores_nonnegative", min(numeric) >= 0, min(numeric))
    check("candidate_count", len(candidates) == 322, len(candidates))
    expected_candidate_surfaces = {row["surface"] for row in current if row["gdt519_rank"] != "1" or row["gdt518_rank"] != row["gdt519_rank"]}
    truth_candidate_surfaces = {row["surface"] for row in candidates if row["candidate_is_truth"] == "YES"}
    check("candidate_truth_coverage", truth_candidate_surfaces == expected_candidate_surfaces, len(truth_candidate_surfaces))
    check("ladder_count", len(ladder) == 15, len(ladder))
    selected_fold = next(row for row in ladder if row["scope"] == "FOUR_FOLD_OLD26_SURFACE_REHEARSAL" and row["model_stage"] == "FOLD_ANCHOR_SELECTED")
    selected_current = next(row for row in ladder if row["scope"] == "CURRENT_159_OLD26_TO_NEW4" and row["anchor_weight"] == "1.0")
    check("ladder_fold_matches", selected_fold["top1_exact_count"] == "1082" and selected_fold["top5_exact_count"] == "1418", selected_fold["top1_exact_count"])
    check("ladder_current_matches", selected_current["top1_exact_count"] == "138" and selected_current["rank_sum"] == "192", selected_current["top1_exact_count"])
    check("known_precedence", all(row["working_policy"].startswith("KNOWN_EVENT_OR_SURFACE_RECIPE_STILL_WINS") for row in current), "all rows")
    check("sealed_pages_absent", all("f84" not in row["physical_pages"] for row in current), "all current page fields")

    failed = [row for row in checks if not row["pass"]]
    validation = {
        "experiment_id": "GDT519",
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
