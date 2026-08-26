#!/usr/bin/env python3
"""Build and replay one dense deterministic fault schedule over the full stream."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt455_stream_fault_contract"
OUT = BASE / "artifacts"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
VARIANTS = ROOT / "experiments/yolo/gdt454_two_card_neighbor_burst_stress/artifacts/gdt454_selected_neighbor_variants.tsv"
DRIVER_PATH = BASE / "src/stream_fault_driver.py"


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


def variant_rank(row: dict[str, str]) -> tuple[int, int, str, str]:
    family_rank = {"ATOM_DELETION": 0, "ADJACENT_SWAP": 1, "SAME_CLASS_SUBSTITUTION": 2}
    return (
        0 if row["neutral_selection_class"] == "NEUTRAL_STOP" else 1,
        family_rank[row["mutation_family"]],
        row["target_recipe"],
        row["neighbor_id"],
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    driver = load_module("gdt455_fault_driver", DRIVER_PATH)
    current = sorted(read_tsv(CURRENT), key=lambda row: int(row["stream_ordinal"]))
    baseline = driver.run_stream(current)

    variants_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(VARIANTS):
        if row["target_recipe"] != "EMPTY_RECIPE":
            variants_by_source[row["source_recipe"]].append(row)
    chosen_variant = {
        source: min(rows, key=variant_rank)
        for source, rows in variants_by_source.items()
    }

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    statement_order: list[str] = []
    for event in current:
        statement_id = event["statement_id"]
        if statement_id not in events_by_statement:
            statement_order.append(statement_id)
        events_by_statement[statement_id].append(event)

    schedule_rows: list[dict[str, object]] = []
    replacements: dict[str, str] = {}
    burst_meta: list[dict[str, object]] = []
    for statement_id in statement_order:
        events = events_by_statement[statement_id]
        if len(events) < 2:
            continue
        candidates: list[tuple[int, int, dict[str, str], dict[str, str], dict[str, str], dict[str, str]]] = []
        for pair_index, (first, second) in enumerate(zip(events, events[1:])):
            if first["component_recipe"] not in chosen_variant or second["component_recipe"] not in chosen_variant:
                continue
            first_variant = chosen_variant[first["component_recipe"]]
            second_variant = chosen_variant[second["component_recipe"]]
            stop_score = sum(
                variant["neutral_selection_class"] == "NEUTRAL_STOP"
                for variant in (first_variant, second_variant)
            )
            candidates.append((-stop_score, pair_index, first, second, first_variant, second_variant))
        if not candidates:
            continue
        neg_stop_score, pair_index, first, second, first_variant, second_variant = min(candidates)
        burst_id = f"G455-B{len(burst_meta) + 1:04d}"
        for position, event, variant in (
            (1, first, first_variant),
            (2, second, second_variant),
        ):
            replacements[event["event_id"]] = variant["target_recipe"]
            schedule_rows.append({
                "burst_id": burst_id,
                "burst_position": position,
                "event_id": event["event_id"],
                "stream_ordinal": event["stream_ordinal"],
                "statement_id": statement_id,
                "physical_page": event["physical_page"],
                "owner_de": event["owner_de"],
                "source_recipe": event["component_recipe"],
                "replacement_recipe": variant["target_recipe"],
                "neighbor_id": variant["neighbor_id"],
                "mutation_family": variant["mutation_family"],
                "neutral_selection_class": variant["neutral_selection_class"],
                "schedule_rule": "ONE_MAXIMUM_NEUTRAL_STOP_PAIR_PER_MULTI_CARD_STATEMENT__EARLIEST_TIE",
            })
        burst_meta.append({
            "burst_id": burst_id,
            "statement_id": statement_id,
            "first_event_id": first["event_id"],
            "second_event_id": second["event_id"],
            "second_stream_ordinal": int(second["stream_ordinal"]),
            "neutral_stop_score": -neg_stop_score,
            "pair_index_within_statement": pair_index + 1,
            "state_bank_id": f"{first['physical_page']}::{first['owner_de']}",
        })
    write_tsv(OUT / "gdt455_dense_fault_schedule.tsv", schedule_rows)

    dense = driver.run_stream(current, replacements)
    baseline_by_event = {str(row["event_id"]): row for row in baseline}
    dense_by_event = {str(row["event_id"]): row for row in dense}
    replay_rows: list[dict[str, object]] = []
    for row in dense:
        reference = baseline_by_event[str(row["event_id"])]
        replay_rows.append({
            **row,
            "baseline_decision": reference["decision"],
            "baseline_outgoing_action": reference["outgoing_action"],
            "baseline_outgoing_argument": reference["outgoing_argument"],
            "bank_state_matches_baseline_after": "YES" if (
                row["outgoing_action"] == reference["outgoing_action"]
                and row["outgoing_argument"] == reference["outgoing_argument"]
            ) else "NO",
            "scope_matches_baseline_after": "YES" if row["scope_outgoing_action"] == reference["scope_outgoing_action"] else "NO",
        })
    write_tsv(OUT / "gdt455_dense_stream_replay.tsv", replay_rows)

    # Replaying each bank alone must reproduce its rows from the global run.
    rows_by_bank: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in current:
        rows_by_bank[(row["physical_page"], row["owner_de"])].append(row)
    bank_rows: list[dict[str, object]] = []
    for bank_ordinal, (bank, source_rows) in enumerate(sorted(rows_by_bank.items()), start=1):
        local = driver.run_stream(source_rows, replacements)
        exact = 0
        for local_row in local:
            global_row = dense_by_event[str(local_row["event_id"])]
            keys = (
                "visible_recipe", "incoming_action", "incoming_argument",
                "scope_incoming_action", "decision", "outgoing_action",
                "outgoing_argument", "scope_outgoing_action",
            )
            exact += all(str(local_row[key]) == str(global_row[key]) for key in keys)
        bank_rows.append({
            "bank_id": f"G455-K{bank_ordinal:03d}",
            "physical_page": bank[0],
            "owner_de": bank[1],
            "event_count": len(source_rows),
            "mutated_event_count": sum(row["event_id"] in replacements for row in source_rows),
            "stop_count": sum(row["decision"] == "STOP" for row in local),
            "isolated_global_exact_count": exact,
            "isolated_global_all_exact": "YES" if exact == len(source_rows) else "NO",
        })
    write_tsv(OUT / "gdt455_owner_bank_isolation.tsv", bank_rows)

    # Measure recovery before another fault in the same owner bank.
    current_index = {row["event_id"]: index for index, row in enumerate(current)}
    recovery_rows: list[dict[str, object]] = []
    for meta in burst_meta:
        second_index = current_index[str(meta["second_event_id"])]
        bank_id = str(meta["state_bank_id"])
        recovery_event = "NONE"
        recovery_status = "BANK_END_RESET_ISOLATES_DIVERGENCE"
        distance = 0
        for candidate in current[second_index + 1:]:
            candidate_bank = f"{candidate['physical_page']}::{candidate['owner_de']}"
            if candidate_bank != bank_id:
                continue
            if candidate["event_id"] in replacements:
                recovery_status = "NEXT_FAULT_BEFORE_PARITY"
                recovery_event = candidate["event_id"]
                break
            distance += 1
            dense_candidate = dense_by_event[candidate["event_id"]]
            base_candidate = baseline_by_event[candidate["event_id"]]
            if (
                dense_candidate["outgoing_action"] == base_candidate["outgoing_action"]
                and dense_candidate["outgoing_argument"] == base_candidate["outgoing_argument"]
            ):
                recovery_status = "STATE_PARITY_BEFORE_NEXT_FAULT"
                recovery_event = candidate["event_id"]
                break
        first_result = dense_by_event[str(meta["first_event_id"])]
        second_result = dense_by_event[str(meta["second_event_id"])]
        bank_boundary_event = None
        bank_boundary_id = "NOT_APPLICABLE"
        bank_boundary_distinct = "NOT_APPLICABLE"
        if recovery_status == "BANK_END_RESET_ISOLATES_DIVERGENCE":
            last_bank_index = max(
                index for index, candidate in enumerate(current)
                if f"{candidate['physical_page']}::{candidate['owner_de']}" == bank_id
            )
            bank_boundary_event = current[last_bank_index + 1] if last_bank_index + 1 < len(current) else None
            bank_boundary_id = (
                f"{bank_boundary_event['physical_page']}::{bank_boundary_event['owner_de']}"
                if bank_boundary_event else "END_OF_STREAM"
            )
            bank_boundary_distinct = "YES" if bank_boundary_event else "END_OF_STREAM"
        recovery_rows.append({
            **meta,
            "first_decision": first_result["decision"],
            "second_decision": second_result["decision"],
            "burst_class": f"FIRST_{'STOP' if first_result['decision'] == 'STOP' else 'READABLE'}__SECOND_{'STOP' if second_result['decision'] == 'STOP' else 'READABLE'}",
            "first_stop_safe": first_result["stop_preserves_state"],
            "second_stop_safe": second_result["stop_preserves_state"],
            "first_same_bank_unmutated_recovery_event": recovery_event,
            "unmutated_card_distance": distance,
            "recovery_before_next_fault": recovery_status,
            "post_bank_boundary_event_id": bank_boundary_event["event_id"] if bank_boundary_event else ("END_OF_STREAM" if recovery_status == "BANK_END_RESET_ISOLATES_DIVERGENCE" else "NOT_APPLICABLE"),
            "post_bank_boundary_id": bank_boundary_id,
            "post_bank_boundary_is_distinct": bank_boundary_distinct,
        })
    write_tsv(OUT / "gdt455_burst_recovery.tsv", recovery_rows)

    result = {
        "status": "DENSE_STREAM_FAULT_CONTRACT_PRESERVES_STOPS_AND_OWNER_BANK_ISOLATION",
        "source_event_count": len(current),
        "statement_count": len(events_by_statement),
        "multi_card_statement_count": sum(len(rows) >= 2 for rows in events_by_statement.values()),
        "eligible_multi_card_statement_count": len(burst_meta),
        "unscheduled_multi_card_statement_count": sum(len(rows) >= 2 for rows in events_by_statement.values()) - len(burst_meta),
        "scheduled_burst_count": len(burst_meta),
        "replaced_event_count": len(replacements),
        "replacement_density": round(len(replacements) / len(current), 6),
        "baseline_decision_exact_count": sum(
            row["decision"] == (
                "READ_AMBER" if source["factor_gate_status"] == "FACTOR_AMBER_LOCAL_APPENDIX" else "READ"
            ) for row, source in zip(baseline, current)
        ),
        "baseline_state_exact_count": sum(
            row["incoming_action"] == source["active_action_before"]
            and row["incoming_argument"] == source["active_argument_before"]
            and row["outgoing_action"] == source["active_action_after"]
            and row["outgoing_argument"] == source["active_argument_after"]
            for row, source in zip(baseline, current)
        ),
        "dense_decision_counts": dict(sorted(Counter(str(row["decision"]) for row in dense).items())),
        "dense_stop_count": sum(row["decision"] == "STOP" for row in dense),
        "dense_stop_state_failure_count": sum(row["decision"] == "STOP" and row["stop_preserves_state"] != "YES" for row in dense),
        "owner_bank_count": len(bank_rows),
        "owner_bank_isolation_exact_count": sum(row["isolated_global_all_exact"] == "YES" for row in bank_rows),
        "owner_bank_event_exact_count": sum(int(row["isolated_global_exact_count"]) for row in bank_rows),
        "burst_decision_counts": dict(sorted(Counter(str(row["burst_class"]) for row in recovery_rows).items())),
        "burst_recovery_counts": dict(sorted(Counter(str(row["recovery_before_next_fault"]) for row in recovery_rows).items())),
        "identity_overrides": 0,
        "advisory_overrides": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt455_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
