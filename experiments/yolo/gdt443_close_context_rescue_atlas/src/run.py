#!/usr/bin/env python3
"""Map every neutral close stop across all incoming action and scope contexts."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
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


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decision(status: str) -> str:
    if status == "FACTOR_GREEN_CROSS_PAGE":
        return "RESCUED_GREEN"
    if status == "FACTOR_AMBER_LOCAL_APPENDIX":
        return "RESCUED_AMBER"
    return "STILL_STOPPED"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reader = load_module("gdt441_reader_for_close_rescue", READER_PATH)
    close_rows = [row for row in read_tsv(STOP_AUDIT) if row["stop_family"] == "CLOSE_CONTEXT"]
    actions = sorted(reader.COMPILER.ACTION_ROOTS)
    modes = [
        ("OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED", "NONE"),
        ("STATEMENT_SCOPE_INHERITED__SAME_HEAD", "HEAD"),
    ]

    matrix: list[dict[str, object]] = []
    for candidate in close_rows:
        recipe = candidate["candidate_recipe"]
        literal = reader.ordered_literal(recipe.split("+"))
        for head in actions:
            for mode, scope_marker in modes:
                scope_head = head if scope_marker == "HEAD" else "NONE"
                gate = reader.gate_recipe(recipe, head, "NONE", scope_head)
                matrix.append({
                    "candidate_recipe": recipe,
                    "candidate_current_status": candidate["current_status"],
                    "source_neighbor_count": candidate["source_neighbor_count"],
                    "incoming_semantic_action": head,
                    "scope_context_mode": mode,
                    "incoming_scope_action": scope_head,
                    "factor_gate_status": gate["factor_gate_status"],
                    "rescue_decision": decision(gate["factor_gate_status"]),
                    "scope_selector_rules": gate["scope_selector_rules"],
                    "portable_factor_rules": gate["portable_factor_rules"],
                    "amber_factor_rules": gate["amber_factor_rules"],
                    "blocked_factor_rules": gate["blocked_factor_rules"],
                    "conditional_literal_reading_de": literal,
                    "surface_or_occurrence_prediction": "NO",
                })
    write_tsv(OUT / "gdt443_936_close_context_rescue_matrix.tsv", matrix, list(matrix[0]))

    by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_head: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in matrix:
        by_recipe[str(row["candidate_recipe"])].append(row)
        by_head[str(row["incoming_semantic_action"])].append(row)
    summaries: list[dict[str, object]] = []
    for candidate in close_rows:
        recipe = candidate["candidate_recipe"]
        rows = by_recipe[recipe]
        counts = Counter(str(row["rescue_decision"]) for row in rows)
        stop_contexts = [
            f"{row['incoming_semantic_action']}@{row['scope_context_mode']}:{row['blocked_factor_rules']}"
            for row in rows if row["rescue_decision"] == "STILL_STOPPED"
        ]
        summaries.append({
            "candidate_recipe": recipe,
            "candidate_current_status": candidate["current_status"],
            "context_count": len(rows),
            "green_context_count": counts["RESCUED_GREEN"],
            "amber_context_count": counts["RESCUED_AMBER"],
            "stop_context_count": counts["STILL_STOPPED"],
            "rescued_context_count": counts["RESCUED_GREEN"] + counts["RESCUED_AMBER"],
            "rescued_under_all_18_contexts": "YES" if counts["STILL_STOPPED"] == 0 else "NO",
            "remaining_stop_contexts": "|".join(stop_contexts) or "NONE",
            "conditional_literal_reading_de": reader.ordered_literal(recipe.split("+")),
        })
    write_tsv(OUT / "gdt443_52_close_candidate_summary.tsv", summaries, list(summaries[0]))

    head_rows: list[dict[str, object]] = []
    for head in actions:
        rows = by_head[head]
        counts = Counter(str(row["rescue_decision"]) for row in rows)
        mode_counts = Counter((str(row["scope_context_mode"]), str(row["rescue_decision"])) for row in rows)
        head_rows.append({
            "incoming_action": head,
            "context_count": len(rows),
            "green_context_count": counts["RESCUED_GREEN"],
            "amber_context_count": counts["RESCUED_AMBER"],
            "stop_context_count": counts["STILL_STOPPED"],
            "owner_scope_green": mode_counts[("OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED", "RESCUED_GREEN")],
            "owner_scope_amber": mode_counts[("OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED", "RESCUED_AMBER")],
            "owner_scope_stop": mode_counts[("OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED", "STILL_STOPPED")],
            "statement_scope_green": mode_counts[("STATEMENT_SCOPE_INHERITED__SAME_HEAD", "RESCUED_GREEN")],
            "statement_scope_amber": mode_counts[("STATEMENT_SCOPE_INHERITED__SAME_HEAD", "RESCUED_AMBER")],
            "statement_scope_stop": mode_counts[("STATEMENT_SCOPE_INHERITED__SAME_HEAD", "STILL_STOPPED")],
        })
    write_tsv(OUT / "gdt443_9_incoming_head_summary.tsv", head_rows, list(head_rows[0]))

    observed_recipes = {row["candidate_recipe"] for row in close_rows if row["current_status"] == "OBSERVED"}
    observed_rows: list[dict[str, object]] = []
    for row in read_tsv(CURRENT):
        if row["component_recipe"] not in observed_recipes:
            continue
        observed_rows.append({
            "event_id": row["event_id"], "physical_page": row["physical_page"],
            "statement_id": row["statement_id"], "register": row["register"],
            "owner_de": row["owner_de"], "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "actual_incoming_action": row["active_action_before"],
            "actual_scope_selectors": row["scope_selector_rules"],
            "actual_factor_gate_status": row["factor_gate_status"],
            "actual_blocked_factor_rules": row["blocked_factor_rules"],
            "actual_reader_status": row["reader_status"],
        })
    write_tsv(OUT / "gdt443_17_observed_close_context_replay.tsv", observed_rows, list(observed_rows[0]))

    status_counts = Counter(row["rescue_decision"] for row in matrix)
    mode_counts = Counter((row["scope_context_mode"], row["rescue_decision"]) for row in matrix)
    result = {
        "status": "FIFTY_ONE_OF_FIFTY_TWO_CLOSE_RECIPES_RESOLVE_IN_ALL_CONTEXTS__TWO_GRADE_III_STOPS_REMAIN",
        "close_candidate_count": len(close_rows),
        "incoming_action_count": len(actions),
        "scope_mode_count": len(modes),
        "rescue_matrix_cell_count": len(matrix),
        "green_cell_count": status_counts["RESCUED_GREEN"],
        "amber_cell_count": status_counts["RESCUED_AMBER"],
        "stop_cell_count": status_counts["STILL_STOPPED"],
        "owner_scope_green_count": mode_counts[("OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED", "RESCUED_GREEN")],
        "owner_scope_amber_count": mode_counts[("OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED", "RESCUED_AMBER")],
        "owner_scope_stop_count": mode_counts[("OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED", "STILL_STOPPED")],
        "statement_scope_green_count": mode_counts[("STATEMENT_SCOPE_INHERITED__SAME_HEAD", "RESCUED_GREEN")],
        "statement_scope_amber_count": mode_counts[("STATEMENT_SCOPE_INHERITED__SAME_HEAD", "RESCUED_AMBER")],
        "statement_scope_stop_count": mode_counts[("STATEMENT_SCOPE_INHERITED__SAME_HEAD", "STILL_STOPPED")],
        "recipes_rescued_in_all_contexts": sum(row["rescued_under_all_18_contexts"] == "YES" for row in summaries),
        "remaining_stop_recipe": next(row["candidate_recipe"] for row in summaries if row["stop_context_count"] != 0),
        "observed_close_recipe_count": len(observed_recipes),
        "observed_close_occurrence_count": len(observed_rows),
        "observed_close_green_count": sum(row["actual_factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" for row in observed_rows),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt443_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
