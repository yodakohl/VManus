#!/usr/bin/env python3
"""Test resynchronization at the first real boundary after terminal stops."""

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
BASE = ROOT / "experiments/yolo/gdt453_terminal_stop_boundary_resynchronization"
OUT = BASE / "artifacts"
GDT452 = ROOT / "experiments/yolo/gdt452_context_stop_actual_next_recovery/artifacts/gdt452_stop_occurrence_recovery.tsv"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
COMMAND_PATH = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py"


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
    if row["factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE":
        return "READ"
    if row["factor_gate_status"] == "FACTOR_AMBER_LOCAL_APPENDIX":
        return "READ_AMBER"
    return "STOP"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    command = load_module("gdt453_integrated_intake", COMMAND_PATH)
    terminal = [row for row in read_tsv(GDT452) if row["immediate_recovery_status"] == "NO_FOLLOWING_CARD"]
    current = sorted(read_tsv(CURRENT), key=lambda row: int(row["stream_ordinal"]))
    current_by_event = {row["event_id"]: row for row in current}
    index_by_event = {row["event_id"]: index for index, row in enumerate(current)}

    def same_scope_next(index: int) -> dict[str, str] | None:
        if index + 1 >= len(current):
            return None
        row = current[index]
        candidate = current[index + 1]
        if candidate["statement_id"] == row["statement_id"] and candidate["physical_page"] == row["physical_page"] and candidate["owner_de"] == row["owner_de"]:
            return candidate
        return None

    rows: list[dict[str, object]] = []
    for source in terminal:
        event = current_by_event[source["event_id"]]
        index = index_by_event[source["event_id"]]
        stop = command.issue_integrated_certificate(
            source["stopped_target_recipe"], source["incoming_action"], source["incoming_argument"],
            source["scope_incoming_action"], "NONE",
        )
        boundary = current[index + 1] if index + 1 < len(current) else None
        if boundary is None:
            boundary_class = "END_OF_STREAM"
            state_source = "NO_BOUNDARY_EVENT"
            boundary_action = str(stop["outgoing_action_v2"])
            boundary_argument = str(stop["outgoing_argument_v2"])
        elif boundary["physical_page"] != event["physical_page"]:
            boundary_class = "NEW_PAGE_OWNER_BANK"
            state_source = "INDEPENDENT_OWNER_BANK"
            boundary_action = boundary["active_action_before"]
            boundary_argument = boundary["active_argument_before"]
        elif boundary["owner_de"] != event["owner_de"]:
            boundary_class = "SAME_PAGE_NEW_OWNER_BANK"
            state_source = "INDEPENDENT_OWNER_BANK"
            boundary_action = boundary["active_action_before"]
            boundary_argument = boundary["active_argument_before"]
        else:
            boundary_class = "SAME_OWNER_NEXT_STATEMENT"
            state_source = "PRESERVED_STOP_STATE_SAME_OWNER"
            boundary_action = str(stop["outgoing_action_v2"])
            boundary_argument = str(stop["outgoing_argument_v2"])

        if boundary is None:
            next_recipe = "NONE"
            decision = "NO_CARD"
            route = "END_OF_STREAM"
            blocked = "NONE"
            status = "NO_BOUNDARY_CARD"
            baseline = "NO_CARD"
            boundary_event_id = "NONE"
            boundary_recipe = "NONE"
        else:
            after_boundary = same_scope_next(index + 1)
            next_recipe = after_boundary["component_recipe"] if after_boundary else "NONE"
            issued = command.issue_integrated_certificate(
                boundary["component_recipe"], boundary_action, boundary_argument, "NONE", next_recipe,
            )
            decision = str(issued["final_execution_decision"])
            route = str(issued["final_execution_route"])
            blocked = str(issued["blocked_factor_rules"])
            status = "BOUNDARY_RECOVERED_GREEN" if decision == "READ" else "BOUNDARY_RECOVERED_AMBER" if decision == "READ_AMBER" else "BOUNDARY_STOP"
            baseline = expected_decision(boundary)
            boundary_event_id = boundary["event_id"]
            boundary_recipe = boundary["component_recipe"]

        rows.append({
            "boundary_recovery_id": f"G453-R{len(rows) + 1:04d}",
            "gdt452_recovery_id": source["recovery_id"],
            "terminal_event_id": source["event_id"],
            "terminal_statement_id": source["statement_id"],
            "terminal_page": source["physical_page"],
            "terminal_owner_de": source["owner_de"],
            "stopped_target_recipe": source["stopped_target_recipe"],
            "stop_blocked_factor_rules": source["stop_blocked_factor_rules"],
            "stop_final_decision": stop["final_execution_decision"],
            "stop_state_preserved": stop["execution_stop_preserves_state"],
            "boundary_class": boundary_class,
            "boundary_state_source": state_source,
            "boundary_incoming_action": boundary_action,
            "boundary_incoming_argument": boundary_argument,
            "boundary_scope_incoming_action": "NONE",
            "boundary_event_id": boundary_event_id,
            "boundary_recipe": boundary_recipe,
            "boundary_next_recipe": next_recipe,
            "boundary_baseline_decision": baseline,
            "boundary_recovery_decision": decision,
            "boundary_recovery_route": route,
            "boundary_blocked_factor_rules": blocked,
            "boundary_recovery_status": status,
            "cross_owner_stop_state_used": "NO" if state_source == "INDEPENDENT_OWNER_BANK" else "NOT_APPLICABLE",
            "meaning_revision": "NO",
            "surface_prediction": "NO",
            "occurrence_prediction": "NO",
        })

    write_tsv(OUT / "gdt453_765_terminal_boundary_recovery.tsv", rows)
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["boundary_class"]), str(row["boundary_state_source"]), str(row["boundary_recovery_status"]))].append(row)
    summary_rows: list[dict[str, object]] = []
    for key, members in sorted(grouped.items()):
        summary_rows.append({
            "boundary_class": key[0],
            "boundary_state_source": key[1],
            "boundary_recovery_status": key[2],
            "occurrence_count": len(members),
            "distinct_terminal_event_count": len({str(row["terminal_event_id"]) for row in members}),
            "distinct_target_recipe_count": len({str(row["stopped_target_recipe"]) for row in members}),
            "distinct_boundary_event_count": len({str(row["boundary_event_id"]) for row in members}),
            "page_count": len({str(row["terminal_page"]) for row in members}),
        })
    write_tsv(OUT / "gdt453_boundary_summary.tsv", summary_rows)

    warnings = [row for row in rows if row["boundary_recovery_status"] in {"BOUNDARY_STOP", "NO_BOUNDARY_CARD"}]
    warning_rows = [{
        "boundary_recovery_id": row["boundary_recovery_id"],
        "terminal_event_id": row["terminal_event_id"],
        "terminal_page": row["terminal_page"],
        "stopped_target_recipe": row["stopped_target_recipe"],
        "boundary_class": row["boundary_class"],
        "boundary_event_id": row["boundary_event_id"],
        "boundary_recipe": row["boundary_recipe"],
        "boundary_blocked_factor_rules": row["boundary_blocked_factor_rules"],
        "boundary_recovery_status": row["boundary_recovery_status"],
    } for row in warnings]
    if not warning_rows:
        warning_rows = [{
            "boundary_recovery_id": "NONE", "terminal_event_id": "NONE", "terminal_page": "NONE",
            "stopped_target_recipe": "NONE", "boundary_class": "NONE", "boundary_event_id": "NONE",
            "boundary_recipe": "NONE", "boundary_blocked_factor_rules": "NONE", "boundary_recovery_status": "NO_WARNINGS",
        }]
    write_tsv(OUT / "gdt453_boundary_warnings.tsv", warning_rows)

    counts = Counter(str(row["boundary_recovery_status"]) for row in rows)
    class_counts = Counter(str(row["boundary_class"]) for row in rows)
    result = {
        "status": "TERMINAL_STOPS_RESYNCHRONIZE_AT_NEXT_AVAILABLE_BOUNDARY",
        "terminal_stop_occurrence_count": len(rows),
        "boundary_class_counts": dict(sorted(class_counts.items())),
        "boundary_recovery_counts": dict(sorted(counts.items())),
        "available_boundary_count": len(rows) - counts["NO_BOUNDARY_CARD"],
        "readable_boundary_count": counts["BOUNDARY_RECOVERED_GREEN"] + counts["BOUNDARY_RECOVERED_AMBER"],
        "boundary_stop_count": counts["BOUNDARY_STOP"],
        "cross_owner_state_leak_count": sum(row["cross_owner_stop_state_used"] == "YES" for row in rows),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt453_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
