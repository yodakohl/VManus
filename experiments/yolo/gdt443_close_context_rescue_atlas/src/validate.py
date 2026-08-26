#!/usr/bin/env python3
"""Validate GDT443's close-context rescue atlas."""

from __future__ import annotations

import csv
import importlib.util
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
BASE = ROOT / "experiments/yolo/gdt443_close_context_rescue_atlas"
OUT = BASE / "artifacts"
READER_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py"
STOP_AUDIT = ROOT / "experiments/yolo/gdt442_forbidden_factor_stop_deck/artifacts/gdt442_269_stop_candidate_audit.tsv"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tracked = [
        OUT / "gdt443_936_close_context_rescue_matrix.tsv",
        OUT / "gdt443_52_close_candidate_summary.tsv",
        OUT / "gdt443_9_incoming_head_summary.tsv",
        OUT / "gdt443_17_observed_close_context_replay.tsv",
        OUT / "gdt443_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(
        ["python3", str(BASE / "src/run.py")], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    after = {path: path.read_bytes() for path in tracked}

    matrix = read_tsv(tracked[0])
    summaries = read_tsv(tracked[1])
    heads = read_tsv(tracked[2])
    observed = read_tsv(tracked[3])
    result = json.loads(tracked[4].read_text(encoding="utf-8"))
    source_close = [row for row in read_tsv(STOP_AUDIT) if row["stop_family"] == "CLOSE_CONTEXT"]
    current = read_tsv(CURRENT)
    reader = load_module("gdt441_reader_for_gdt443_validation", READER_PATH)

    matrix_keys = {
        (row["candidate_recipe"], row["incoming_semantic_action"], row["scope_context_mode"])
        for row in matrix
    }
    matrix_decisions = Counter(row["rescue_decision"] for row in matrix)
    mode_decisions = Counter((row["scope_context_mode"], row["rescue_decision"]) for row in matrix)
    stop_rows = [row for row in matrix if row["rescue_decision"] == "STILL_STOPPED"]
    observed_source = [row for row in current if row["component_recipe"] in {item["candidate_recipe"] for item in source_close if item["current_status"] == "OBSERVED"}]

    recompute = []
    for row in matrix:
        gate = reader.gate_recipe(
            row["candidate_recipe"], row["incoming_semantic_action"], "NONE",
            row["incoming_scope_action"],
        )
        recompute.append(all(gate[field] == row[field] for field in (
            "factor_gate_status", "scope_selector_rules", "portable_factor_rules",
            "amber_factor_rules", "blocked_factor_rules",
        )))

    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)
    checks = {
        "source_close_52_unique": len(source_close) == len({row["candidate_recipe"] for row in source_close}) == 52,
        "matrix_936_unique": len(matrix) == len(matrix_keys) == 936,
        "matrix_recipe_set_exact": {row["candidate_recipe"] for row in matrix} == {row["candidate_recipe"] for row in source_close},
        "matrix_nine_heads": {row["incoming_semantic_action"] for row in matrix} == reader.COMPILER.ACTION_ROOTS,
        "matrix_two_modes": {row["scope_context_mode"] for row in matrix} == {"OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED", "STATEMENT_SCOPE_INHERITED__SAME_HEAD"},
        "matrix_counts_841_93_2": matrix_decisions == {"RESCUED_GREEN": 841, "RESCUED_AMBER": 93, "STILL_STOPPED": 2},
        "owner_scope_counts_387_81_0": {
            decision: count for (mode, decision), count in mode_decisions.items()
            if mode == "OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED"
        } == {"RESCUED_GREEN": 387, "RESCUED_AMBER": 81},
        "statement_scope_counts_454_12_2": {
            decision: count for (mode, decision), count in mode_decisions.items()
            if mode == "STATEMENT_SCOPE_INHERITED__SAME_HEAD"
        } == {"RESCUED_GREEN": 454, "RESCUED_AMBER": 12, "STILL_STOPPED": 2},
        "two_stops_exact": {
            (row["candidate_recipe"], row["incoming_semantic_action"], row["scope_context_mode"], row["blocked_factor_rules"])
            for row in stop_rows
        } == {
            ("OL+EEE+DY", "CHD", "STATEMENT_SCOPE_INHERITED__SAME_HEAD", "FOCUS:CHD<-EEE"),
            ("OL+EEE+DY", "R", "STATEMENT_SCOPE_INHERITED__SAME_HEAD", "FOCUS:R<-EEE"),
        },
        "all_owner_scope_rescued": all(row["rescue_decision"] != "STILL_STOPPED" for row in matrix if row["scope_context_mode"].startswith("OWNER_SCOPE")),
        "matrix_recomputes": all(recompute),
        "matrix_no_prediction": all(row["surface_or_occurrence_prediction"] == "NO" for row in matrix),
        "summaries_52_unique": len(summaries) == len({row["candidate_recipe"] for row in summaries}) == 52,
        "summary_contexts_18_each": all(int(row["context_count"]) == 18 for row in summaries),
        "summary_51_full_one_partial": Counter(row["rescued_under_all_18_contexts"] for row in summaries) == {"YES": 51, "NO": 1},
        "summary_partial_exact": [(row["candidate_recipe"], row["green_context_count"], row["amber_context_count"], row["stop_context_count"]) for row in summaries if row["rescued_under_all_18_contexts"] == "NO"] == [("OL+EEE+DY", "15", "1", "2")],
        "head_summary_9_unique": len(heads) == len({row["incoming_action"] for row in heads}) == 9,
        "head_summary_104_each": all(int(row["context_count"]) == 104 for row in heads),
        "head_only_chd_r_stop": {row["incoming_action"] for row in heads if int(row["stop_context_count"])} == {"CHD", "R"},
        "observed_17_exact": len(observed) == len({row["event_id"] for row in observed}) == 17,
        "observed_six_recipes": len({row["component_recipe"] for row in observed}) == 6,
        "observed_matches_current": {row["event_id"] for row in observed} == {row["event_id"] for row in observed_source},
        "observed_all_green": all(row["actual_factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" and row["actual_blocked_factor_rules"] == "NONE" for row in observed),
        "observed_eight_pages": len({row["physical_page"] for row in observed}) == 8,
        "result_status_exact": result["status"] == "FIFTY_ONE_OF_FIFTY_TWO_CLOSE_RECIPES_RESOLVE_IN_ALL_CONTEXTS__TWO_GRADE_III_STOPS_REMAIN",
        "result_matrix_counts_exact": result["close_candidate_count"] == 52 and result["incoming_action_count"] == 9 and result["scope_mode_count"] == 2 and result["rescue_matrix_cell_count"] == 936 and result["green_cell_count"] == 841 and result["amber_cell_count"] == 93 and result["stop_cell_count"] == 2,
        "result_mode_counts_exact": [result["owner_scope_green_count"], result["owner_scope_amber_count"], result["owner_scope_stop_count"], result["statement_scope_green_count"], result["statement_scope_amber_count"], result["statement_scope_stop_count"]] == [387, 81, 0, 454, 12, 2],
        "result_recipe_observed_exact": result["recipes_rescued_in_all_contexts"] == 51 and result["remaining_stop_recipe"] == "OL+EEE+DY" and result["observed_close_recipe_count"] == 6 and result["observed_close_occurrence_count"] == result["observed_close_green_count"] == 17,
        "result_no_expansion": result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt443_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
