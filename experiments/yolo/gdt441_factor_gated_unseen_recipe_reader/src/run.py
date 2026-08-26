#!/usr/bin/env python3
"""Build and audit the factor-gated unseen-recipe fallback."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader"
OUT = BASE / "artifacts"
EVENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_4576_event_owner_local_edition.tsv"
GDT440_EVENTS = ROOT / "experiments/yolo/gdt440_dual_channel_order_trace_reader/artifacts/gdt440_4576_dual_channel_stream_readings.tsv"
GDT438_EVENTS = ROOT / "experiments/yolo/gdt438_order_safe_streaming_reader/artifacts/gdt438_4576_order_safe_stream_readings.tsv"
PRIVATE = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_861_page_private_recipe_replay.tsv"
CANDIDATES = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_4938_candidate_density.tsv"
READER = BASE / "src/factor_gate_stream_read.py"


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


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reader = load_module("gdt441_factor_gate_reader", READER)
    streamed = reader.stream_rows(read_tsv(EVENTS))
    gdt440 = {row["event_id"]: row for row in read_tsv(GDT440_EVENTS)}
    current_rows: list[dict[str, object]] = []
    for row in streamed:
        old = gdt440[str(row["event_id"])]
        current_rows.append({
            **row,
            "state_clause_literal_match_gdt440": "YES" if (
                row["reader_clause_de"] == old["order_safe_clause_de"]
                and row["ordered_literal_reading_de"] == old["ordered_literal_reading_de"]
            ) else "NO",
        })
    write_tsv(OUT / "gdt441_4576_factor_reader_replay.tsv", current_rows, list(current_rows[0]))

    current_by_page_recipe: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in current_rows:
        current_by_page_recipe.setdefault((str(row["physical_page"]), str(row["component_recipe"])), []).append(row)
    private_rows: list[dict[str, object]] = []
    for row in read_tsv(PRIVATE):
        event = current_by_page_recipe[(row["held_page"], row["private_target_recipe"])][-1]
        gate = {
            field: str(event[field]) for field in (
                "factor_gate_status", "scope_selector_rules", "portable_factor_rules",
                "amber_factor_rules", "blocked_factor_rules",
            )
        }
        atoms = row["private_target_recipe"].split("+")
        literal = reader.ordered_literal(atoms)
        private_rows.append({
            **row,
            "sample_event_id": event["event_id"],
            "sample_incoming_action": event["active_action_before"],
            **gate,
            "factor_conditional_reading_de": literal,
            "factor_replay_decision": "READ_GREEN" if gate["factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" else "READ_AMBER" if gate["factor_gate_status"] == "FACTOR_AMBER_LOCAL_APPENDIX" else "STOP",
            "occurrence_prediction": "NO__VISIBLE_RECIPE_REQUIRED",
        })
    write_tsv(OUT / "gdt441_861_page_private_factor_replay.tsv", private_rows, list(private_rows[0]))

    candidate_rows: list[dict[str, object]] = []
    for row in read_tsv(CANDIDATES):
        gate = reader.gate_recipe(row["candidate_recipe"], "NONE")
        candidate_rows.append({
            "candidate_recipe": row["candidate_recipe"],
            "current_status": row["current_status"],
            "source_neighbor_count": row["source_neighbor_count"],
            **gate,
            "factor_gate_is_occurrence_prediction": "NO",
        })
    write_tsv(OUT / "gdt441_4938_candidate_factor_gate.tsv", candidate_rows, list(candidate_rows[0]))

    inventory_rows = [
        {"factor_family": "PORTABLE_FOCUS_EDGE", "rule_count": len(reader.PORTABLE_FOCUS_EDGES), "rules": "|".join(sorted(reader.PORTABLE_FOCUS_EDGES)), "future_status": "GREEN"},
        {"factor_family": "LOCAL_FOCUS_EDGE", "rule_count": len(reader.LOCAL_FOCUS_EDGES), "rules": "|".join(sorted(reader.LOCAL_FOCUS_EDGES)), "future_status": "AMBER"},
        {"factor_family": "LOCAL_OWNER_FOCUS_EDGE", "rule_count": len(reader.LOCAL_OWNER_FOCUS_EDGES), "rules": "|".join(sorted(reader.LOCAL_OWNER_FOCUS_EDGES)), "future_status": "AMBER"},
        {"factor_family": "PORTABLE_ADJACENT_ACTION_PAIR", "rule_count": len(reader.PORTABLE_ACTION_PAIRS), "rules": "|".join(sorted(reader.PORTABLE_ACTION_PAIRS)), "future_status": "GREEN"},
        {"factor_family": "LOCAL_ADJACENT_ACTION_PAIR", "rule_count": len(reader.LOCAL_ACTION_PAIRS), "rules": "|".join(sorted(reader.LOCAL_ACTION_PAIRS)), "future_status": "AMBER"},
        {"factor_family": "PORTABLE_CLOSE_TARGET", "rule_count": len(reader.PORTABLE_CLOSE_TARGETS), "rules": "|".join(sorted(reader.PORTABLE_CLOSE_TARGETS)), "future_status": "GREEN"},
        {"factor_family": "R_POSITIONAL_TOPOLOGY", "rule_count": 1, "rules": "R<-E", "future_status": "GREEN"},
    ]
    write_tsv(OUT / "gdt441_factor_gate_inventory.tsv", inventory_rows, list(inventory_rows[0]))

    private_counts = Counter(row["factor_replay_decision"] for row in private_rows)
    candidate_counts = Counter((row["current_status"], row["factor_gate_status"]) for row in candidate_rows)
    accepted_absent = sum(
        count for (status, gate), count in candidate_counts.items()
        if status == "ABSENT" and gate != "STOP__UNLICENSED_FACTOR"
    )
    result = {
        "status": "ALL_PAGE_PRIVATE_RECIPES_CONDITIONALLY_READABLE__NOT_OCCURRENCE_PREDICTION",
        "current_event_count": len(current_rows),
        "current_exact_replay_match_count": sum(row["state_clause_literal_match_gdt440"] == "YES" for row in current_rows),
        "page_private_recipe_count": len(private_rows),
        "page_private_green_count": private_counts["READ_GREEN"],
        "page_private_amber_count": private_counts["READ_AMBER"],
        "page_private_stop_count": private_counts["STOP"],
        "candidate_recipe_count": len(candidate_rows),
        "absent_candidate_factor_accepted_count": accepted_absent,
        "factor_gate_occurrence_prediction": False,
        "portable_focus_edge_count": len(reader.PORTABLE_FOCUS_EDGES),
        "local_focus_edge_count": len(reader.LOCAL_FOCUS_EDGES),
        "local_owner_focus_edge_count": len(reader.LOCAL_OWNER_FOCUS_EDGES),
        "portable_action_pair_count": len(reader.PORTABLE_ACTION_PAIRS),
        "local_action_pair_count": len(reader.LOCAL_ACTION_PAIRS),
        "portable_close_target_count": len(reader.PORTABLE_CLOSE_TARGETS),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt441_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
