#!/usr/bin/env python3
"""Replay the actual following source card after every GDT448 context stop."""

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
BASE = ROOT / "experiments/yolo/gdt452_context_stop_actual_next_recovery"
OUT = BASE / "artifacts"
COMMAND_PATH = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py"
CURRENT_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
REPLAY_DIR = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay/artifacts"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_decision(row: dict[str, str]) -> str:
    status = row["factor_gate_status"]
    if status == "FACTOR_GREEN_CROSS_PAGE":
        return "READ"
    if status == "FACTOR_AMBER_LOCAL_APPENDIX":
        return "READ_AMBER"
    return "STOP"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    command = load_module("gdt452_integrated_intake", COMMAND_PATH)
    current = sorted(read_tsv(CURRENT_PATH), key=lambda row: int(row["stream_ordinal"]))
    current_by_event = {row["event_id"]: row for row in current}
    current_index = {row["event_id"]: index for index, row in enumerate(current)}

    def following(event_id: str) -> dict[str, str] | None:
        index = current_index[event_id]
        if index + 1 >= len(current):
            return None
        row = current[index]
        candidate = current[index + 1]
        same_scope = (
            candidate["statement_id"] == row["statement_id"]
            and candidate["physical_page"] == row["physical_page"]
            and candidate["owner_de"] == row["owner_de"]
        )
        return candidate if same_scope else None

    def following_same_owner(event_id: str) -> dict[str, str] | None:
        index = current_index[event_id]
        if index + 1 >= len(current):
            return None
        row = current[index]
        candidate = current[index + 1]
        return candidate if candidate["physical_page"] == row["physical_page"] and candidate["owner_de"] == row["owner_de"] else None

    replay = [
        row
        for path in sorted(REPLAY_DIR.glob("gdt448_context_neighbor_replay_part*.tsv"))
        for row in read_tsv(path)
    ]
    stop_probes = [row for row in replay if row["context_execution_decision"] == "STOP"]
    occurrence_rows: list[dict[str, object]] = []
    stop_reissue_matches = 0
    stop_state_safe = 0
    source_next_alignment = 0

    for stop_row in stop_probes:
        event_ids = stop_row["context_event_ids"].split("|")
        for event_id in event_ids:
            source_event = current_by_event[event_id]
            stop = command.issue_integrated_certificate(
                stop_row["target_recipe"],
                stop_row["incoming_action"],
                stop_row["incoming_argument"],
                stop_row["scope_incoming_action"],
                stop_row["next_recipe"],
            )
            stop_reissue_matches += stop["final_execution_decision"] == "STOP"
            stop_state_safe += stop["execution_stop_preserves_state"] == "YES"

            next_event = following(event_id)
            actual_next_recipe = next_event["component_recipe"] if next_event else "NONE"
            if actual_next_recipe == stop_row["next_recipe"]:
                source_next_alignment += 1
            next_next_event = following(next_event["event_id"]) if next_event else None
            next_next_recipe = next_next_event["component_recipe"] if next_next_event else "NONE"
            cascade_event_id = "NONE"
            cascade_recipe = "NONE"
            cascade_decision = "NOT_APPLICABLE"
            cascade_route = "NOT_APPLICABLE"
            cascade_blocked = "NONE"
            cascade_resolution = "NOT_APPLICABLE"

            if next_event is None:
                recovery_decision = "NO_CARD"
                recovery_route = "NO_FOLLOWING_SOURCE_CARD_IN_SAME_SCOPE"
                recovery_blocked = "NONE"
                recovery_identity = "NONE"
                recovery_history = "NONE"
                recovery_action_after = str(stop["outgoing_action_v2"])
                recovery_argument_after = str(stop["outgoing_argument_v2"])
                recovery_status = "NO_FOLLOWING_CARD"
                expected = "NO_CARD"
            else:
                recovery = command.issue_integrated_certificate(
                    actual_next_recipe,
                    str(stop["outgoing_action_v2"]),
                    str(stop["outgoing_argument_v2"]),
                    stop_row["scope_incoming_action"],
                    next_next_recipe,
                )
                recovery_decision = str(recovery["final_execution_decision"])
                recovery_route = str(recovery["final_execution_route"])
                recovery_blocked = str(recovery["blocked_factor_rules"])
                recovery_identity = str(recovery["identity_route"])
                recovery_history = str(recovery["advisory_history_status"])
                recovery_action_after = str(recovery["outgoing_action_v2"])
                recovery_argument_after = str(recovery["outgoing_argument_v2"])
                recovery_status = "RECOVERED_GREEN" if recovery_decision == "READ" else "RECOVERED_AMBER" if recovery_decision == "READ_AMBER" else "RECOVERY_STOP"
                expected = expected_decision(next_event)
                if recovery_decision == "STOP":
                    boundary_event = following_same_owner(next_event["event_id"])
                    if boundary_event is None or boundary_event["statement_id"] == next_event["statement_id"]:
                        cascade_resolution = "NO_NEW_STATEMENT_RECOVERY_CARD"
                    else:
                        boundary_next = following(boundary_event["event_id"])
                        boundary_next_recipe = boundary_next["component_recipe"] if boundary_next else "NONE"
                        boundary = command.issue_integrated_certificate(
                            boundary_event["component_recipe"],
                            recovery_action_after,
                            recovery_argument_after,
                            "NONE",
                            boundary_next_recipe,
                        )
                        cascade_event_id = boundary_event["event_id"]
                        cascade_recipe = boundary_event["component_recipe"]
                        cascade_decision = str(boundary["final_execution_decision"])
                        cascade_route = str(boundary["final_execution_route"])
                        cascade_blocked = str(boundary["blocked_factor_rules"])
                        cascade_resolution = "RECOVERED_AT_NEXT_STATEMENT" if cascade_decision in {"READ", "READ_AMBER"} else "CASCADE_CONTINUES_AFTER_STATEMENT_RESET"

            occurrence_rows.append({
                "recovery_id": f"G452-R{len(occurrence_rows) + 1:05d}",
                "replay_id": stop_row["replay_id"],
                "neighbor_id": stop_row["neighbor_id"],
                "context_id": stop_row["context_id"],
                "event_id": event_id,
                "statement_id": source_event["statement_id"],
                "physical_page": source_event["physical_page"],
                "owner_de": source_event["owner_de"],
                "source_recipe": stop_row["source_recipe"],
                "stopped_target_recipe": stop_row["target_recipe"],
                "mutation_family": stop_row["mutation_family"],
                "incoming_action": stop_row["incoming_action"],
                "incoming_argument": stop_row["incoming_argument"],
                "scope_incoming_action": stop_row["scope_incoming_action"],
                "stop_blocked_factor_rules": stop_row["context_blocked_factor_rules"],
                "stop_final_decision": stop["final_execution_decision"],
                "stop_state_preserved": stop["execution_stop_preserves_state"],
                "actual_next_available": "YES" if next_event else "NO",
                "next_event_id": next_event["event_id"] if next_event else "NONE",
                "actual_next_recipe": actual_next_recipe,
                "next_next_recipe": next_next_recipe,
                "source_next_recipe_alignment": "YES" if actual_next_recipe == stop_row["next_recipe"] else "NO",
                "actual_next_baseline_decision": expected,
                "recovery_decision_after_stop": recovery_decision,
                "recovery_route": recovery_route,
                "recovery_blocked_factor_rules": recovery_blocked,
                "recovery_identity_route": recovery_identity,
                "recovery_advisory_history": recovery_history,
                "recovery_action_after": recovery_action_after,
                "recovery_argument_after": recovery_argument_after,
                "immediate_recovery_status": recovery_status,
                "cascade_boundary_event_id": cascade_event_id,
                "cascade_boundary_recipe": cascade_recipe,
                "cascade_boundary_decision": cascade_decision,
                "cascade_boundary_route": cascade_route,
                "cascade_boundary_blocked_factor_rules": cascade_blocked,
                "cascade_resolution_status": cascade_resolution,
                "identity_can_override": "NO",
                "advisory_can_override": "NO",
                "meaning_revision": "NO",
                "surface_prediction": "NO",
                "occurrence_prediction": "NO",
            })

    write_tsv(OUT / "gdt452_stop_occurrence_recovery.tsv", occurrence_rows)

    summary_groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        key = (
            str(row["stop_blocked_factor_rules"]),
            str(row["mutation_family"]),
            str(row["immediate_recovery_status"]),
        )
        summary_groups[key].append(row)
    summary_rows: list[dict[str, object]] = []
    for key, rows in sorted(summary_groups.items()):
        summary_rows.append({
            "stop_blocked_factor_rules": key[0],
            "mutation_family": key[1],
            "immediate_recovery_status": key[2],
            "occurrence_count": len(rows),
            "distinct_stop_probe_count": len({str(row["replay_id"]) for row in rows}),
            "distinct_target_recipe_count": len({str(row["stopped_target_recipe"]) for row in rows}),
            "distinct_following_recipe_count": len({str(row["actual_next_recipe"]) for row in rows}),
            "physical_page_count": len({str(row["physical_page"]) for row in rows}),
        })
    write_tsv(OUT / "gdt452_recovery_summary.tsv", summary_rows)

    exception_rows = [row for row in occurrence_rows if row["immediate_recovery_status"] in {"RECOVERY_STOP", "NO_FOLLOWING_CARD"}]
    if not exception_rows:
        exception_rows = [{
            "recovery_id": "NONE",
            "event_id": "NONE",
            "physical_page": "NONE",
            "stopped_target_recipe": "NONE",
            "stop_blocked_factor_rules": "NONE",
            "actual_next_recipe": "NONE",
            "recovery_blocked_factor_rules": "NONE",
            "immediate_recovery_status": "NO_EXCEPTIONS",
        }]
    else:
        exception_rows = [{
            "recovery_id": row["recovery_id"],
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "stopped_target_recipe": row["stopped_target_recipe"],
            "stop_blocked_factor_rules": row["stop_blocked_factor_rules"],
            "actual_next_recipe": row["actual_next_recipe"],
            "recovery_blocked_factor_rules": row["recovery_blocked_factor_rules"],
            "immediate_recovery_status": row["immediate_recovery_status"],
            "cascade_boundary_event_id": row["cascade_boundary_event_id"],
            "cascade_boundary_recipe": row["cascade_boundary_recipe"],
            "cascade_boundary_decision": row["cascade_boundary_decision"],
            "cascade_resolution_status": row["cascade_resolution_status"],
        } for row in exception_rows]
    write_tsv(OUT / "gdt452_recovery_exceptions.tsv", exception_rows)

    recovery_counts = Counter(str(row["immediate_recovery_status"]) for row in occurrence_rows)
    unique_scenarios = {
        (
            str(row["stopped_target_recipe"]), str(row["event_id"]),
            str(row["incoming_action"]), str(row["incoming_argument"]),
            str(row["scope_incoming_action"]), str(row["actual_next_recipe"]),
        )
        for row in occurrence_rows
    }
    result = {
        "status": "ACTUAL_NEXT_CARD_RECOVERY_AUDITED_AFTER_ALL_CONTEXT_STOPS",
        "stop_probe_count": len(stop_probes),
        "expanded_stop_occurrence_count": len(occurrence_rows),
        "unique_stop_scenario_count": len(unique_scenarios),
        "stop_reissue_match_count": stop_reissue_matches,
        "stop_state_safe_count": stop_state_safe,
        "source_next_alignment_count": source_next_alignment,
        "immediate_recovery_counts": dict(sorted(recovery_counts.items())),
        "immediate_readable_recovery_count": recovery_counts["RECOVERED_GREEN"] + recovery_counts["RECOVERED_AMBER"],
        "immediate_recovery_stop_count": recovery_counts["RECOVERY_STOP"],
        "no_following_card_count": recovery_counts["NO_FOLLOWING_CARD"],
        "dependent_close_cascade_count": sum(row["immediate_recovery_status"] == "RECOVERY_STOP" for row in occurrence_rows),
        "next_statement_recovery_count": sum(row["cascade_resolution_status"] == "RECOVERED_AT_NEXT_STATEMENT" for row in occurrence_rows),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt452_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
