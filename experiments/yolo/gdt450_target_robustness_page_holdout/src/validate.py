#!/usr/bin/env python3
"""Validate target-robustness leave-one-page-out replay."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt450_target_robustness_page_holdout"
OUT = BASE / "artifacts"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    shard_paths = sorted(OUT.glob("gdt450_target_page_folds_part*.tsv"))
    tracked = [
        *shard_paths,
        OUT / "gdt450_false_safe_cases.tsv",
        OUT / "gdt450_page_holdout_summary.tsv",
        OUT / "gdt450_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    rebuilt_shards = sorted(OUT.glob("gdt450_target_page_folds_part*.tsv"))
    after_paths = [*rebuilt_shards, tracked[-3], tracked[-2], tracked[-1]]
    after = {path: path.read_bytes() for path in after_paths}

    folds = [row for path in rebuilt_shards for row in read_tsv(path)]
    critical = read_tsv(OUT / "gdt450_false_safe_cases.tsv")
    pages = read_tsv(OUT / "gdt450_page_holdout_summary.tsv")
    result = json.loads((OUT / "gdt450_result.json").read_text(encoding="utf-8"))
    outcomes = Counter(row["holdout_outcome"] for row in folds)
    unseen = Counter(row["unseen_context_outcome"] for row in folds)
    false_safe_folds = {row["fold_id"] for row in folds if row["holdout_outcome"] == "FALSE_SAFE"}
    critical_folds = {row["fold_id"] for row in critical}
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in after_paths)

    checks = {
        "eight_shards_35577_folds": len(rebuilt_shards) == 8 and sum(len(read_tsv(path)) for path in rebuilt_shards) == 35577 and all(len(read_tsv(path)) == 5000 for path in rebuilt_shards[:-1]) and len(read_tsv(rebuilt_shards[-1])) == 577,
        "fold_ids_unique_contiguous": len(folds) == len({row["fold_id"] for row in folds}) == 35577 and [row["fold_id"] for row in folds] == [f"G450-F{i:06d}" for i in range(1, 35578)],
        "target_page_pairs_unique": len({(row["target_recipe"], row["held_page"]) for row in folds}) == 35577,
        "twenty_four_physical_pages": len(pages) == len({row["held_page"] for row in pages}) == 24 and {row["held_page"] for row in pages} == {row["held_page"] for row in folds},
        "outcomes_exact": outcomes == {"CORRECT_READABLE": 20052, "CORRECT_STOP": 2400, "FALSE_SAFE": 8, "FALSE_STOP": 2, "ABSTAIN_TRAIN_MIXED": 53, "NO_OTHER_PAGE_TRAINING": 13062},
        "unseen_outcomes_exact": unseen == {"CORRECT_READABLE": 19591, "CORRECT_STOP": 2362, "FALSE_SAFE": 8, "FALSE_STOP": 2, "ABSTAIN_TRAIN_MIXED": 42, "NO_OTHER_PAGE_TRAINING": 13062, "NO_UNSEEN_HELD_CONTEXT": 510},
        "fold_decision_counts_internal": all(int(row["training_green_count"]) + int(row["training_amber_count"]) + int(row["training_stop_count"]) == int(row["training_occurrence_probe_count"]) and int(row["held_green_count"]) + int(row["held_amber_count"]) + int(row["held_stop_count"]) == int(row["held_occurrence_probe_count"]) for row in folds),
        "false_safe_eight_unique": len(critical) == len({row["critical_id"] for row in critical}) == len({row["event_id"] for row in critical}) == 8,
        "false_safe_folds_bound_exact": critical_folds == false_safe_folds and len(false_safe_folds) == 8,
        "false_safe_targets_exact": {row["target_recipe"] for row in critical} == {"D_ADDR+EEE+Y", "E+DY", "EE+DY", "EEE+Y", "OT+EEE+AIIN", "OT+EEE+O", "OT+EEE+OR", "OT+O+DY"},
        "false_safe_pages_exact": {row["held_page"] for row in critical} == {"f72r", "f76r", "f82r", "f83r", "f88v"},
        "false_safe_rules_only_known": Counter(row["blocked_factor_rules"] for row in critical) == {"FOCUS:CHD<-EEE": 5, "CLOSE:NO_ACTIVE_ACTION": 3},
        "false_safe_live_stop_override": all(row["training_shortcut_class"] == "READABLE" and row["live_certificate_decision"] == "STOP" and row["required_action"] == "LIVE_CERTIFICATE_OVERRIDES_SHORTCUT__STOP" for row in critical),
        "all_false_safe_unseen_context": all(row["unseen_context_outcome"] == "FALSE_SAFE" for row in folds if row["holdout_outcome"] == "FALSE_SAFE"),
        "two_false_stops_exact": {(row["held_page"], row["target_recipe"]) for row in folds if row["holdout_outcome"] == "FALSE_STOP"} == {("f95v", "OT+EEE+AIIN"), ("f72r", "OT+EEE+O")},
        "all_shortcuts_nonoverriding": all(row["shortcut_never_overrides_live_certificate"] == "YES" and row["identity_not_inferred"] == "YES" and row["occurrence_not_predicted"] == "YES" for row in folds),
        "page_summaries_cover_folds": sum(int(row["target_fold_count"]) for row in pages) == 35577 and sum(int(row["false_safe_count"]) for row in pages) == 8 and sum(int(row["false_stop_count"]) for row in pages) == 2,
        "result_status_exact": result["status"] == "PAGE_HOLDOUT_REJECTS_ROBUSTNESS_SHORTCUT_AS_EXECUTION_OVERRIDE",
        "result_counts_exact": result["raw_weighted_occurrence_probe_count"] == result["unique_target_event_probe_count"] == 65746 and result["unique_target_count"] == 18381 and result["target_page_fold_count"] == 35577 and result["physical_page_count"] == 24,
        "result_outcomes_exact": result["holdout_outcome_counts"] == dict(sorted(outcomes.items())) and result["unseen_context_outcome_counts"] == dict(sorted(unseen.items())),
        "result_false_safe_exact": result["false_safe_fold_count"] == result["false_safe_stop_occurrence_count"] == result["false_safe_target_count"] == result["unseen_context_false_safe_fold_count"] == 8 and result["false_safe_page_count"] == 5,
        "result_no_expansion": result["shortcut_execution_overrides_allowed"] == result["identity_promotions"] == result["meaning_revisions"] == result["surface_predictions"] == result["occurrence_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": set(before) == set(after) and before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "failed_checks": failed,
        "checks": checks,
    }
    (OUT / "gdt450_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
