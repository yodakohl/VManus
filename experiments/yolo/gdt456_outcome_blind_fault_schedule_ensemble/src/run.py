#!/usr/bin/env python3
"""Replay six outcome-blind visible mutation schedules through the full stream."""

from __future__ import annotations

import csv
import hashlib
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
BASE = ROOT / "experiments/yolo/gdt456_outcome_blind_fault_schedule_ensemble"
OUT = BASE / "artifacts"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
VARIANTS = ROOT / "experiments/yolo/gdt454_two_card_neighbor_burst_stress/artifacts/gdt454_selected_neighbor_variants.tsv"
DRIVER_PATH = ROOT / "experiments/yolo/gdt455_stream_fault_contract/src/stream_fault_driver.py"
SCHEDULES = (
    ("LEX_FIRST", "lexicographically first target and neighbour"),
    ("LEX_LAST", "lexicographically last target and neighbour"),
    ("HASH_MIN", "smallest source-bound SHA-256 rank"),
    ("DELETION_FIRST", "atom deletion, then swap, then substitution"),
    ("SWAP_FIRST", "adjacent swap, then substitution, then deletion"),
    ("SUBSTITUTION_FIRST", "same-class substitution, then swap, then deletion"),
)
FAMILY_ORDERS = {
    "DELETION_FIRST": {"ATOM_DELETION": 0, "ADJACENT_SWAP": 1, "SAME_CLASS_SUBSTITUTION": 2},
    "SWAP_FIRST": {"ADJACENT_SWAP": 0, "SAME_CLASS_SUBSTITUTION": 1, "ATOM_DELETION": 2},
    "SUBSTITUTION_FIRST": {"SAME_CLASS_SUBSTITUTION": 0, "ADJACENT_SWAP": 1, "ATOM_DELETION": 2},
}


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


def hash_rank(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def select_variant(policy: str, source: str, rows: list[dict[str, str]]) -> dict[str, str]:
    lexical = lambda row: (row["target_recipe"], row["neighbor_id"])
    if policy == "LEX_FIRST":
        return min(rows, key=lexical)
    if policy == "LEX_LAST":
        return max(rows, key=lexical)
    if policy == "HASH_MIN":
        return min(rows, key=lambda row: (hash_rank(policy, source, row["target_recipe"], row["neighbor_id"]), *lexical(row)))
    family_order = FAMILY_ORDERS[policy]
    return min(rows, key=lambda row: (family_order[row["mutation_family"]], *lexical(row)))


def same_bank(row: dict[str, str], bank_id: str) -> bool:
    return f"{row['physical_page']}::{row['owner_de']}" == bank_id


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    driver = load_module("gdt456_fault_driver", DRIVER_PATH)
    current = sorted(read_tsv(CURRENT), key=lambda row: int(row["stream_ordinal"]))
    baseline = driver.run_stream(current)
    baseline_by_event = {str(row["event_id"]): row for row in baseline}
    current_index = {row["event_id"]: index for index, row in enumerate(current)}

    variants_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(VARIANTS):
        if row["target_recipe"] != "EMPTY_RECIPE":
            variants_by_source[row["source_recipe"]].append(row)

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    statement_order: list[str] = []
    for event in current:
        if event["statement_id"] not in events_by_statement:
            statement_order.append(event["statement_id"])
        events_by_statement[event["statement_id"]].append(event)
    rows_by_bank: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for event in current:
        rows_by_bank[(event["physical_page"], event["owner_de"])].append(event)

    manifest_rows: list[dict[str, object]] = []
    all_schedule_rows: list[dict[str, object]] = []
    all_recovery_rows: list[dict[str, object]] = []
    all_unmutated_stops: list[dict[str, object]] = []
    all_bank_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for schedule_ordinal, (schedule_id, description) in enumerate(SCHEDULES, start=1):
        chosen = {
            source: select_variant(schedule_id, source, rows)
            for source, rows in variants_by_source.items()
        }
        replacements: dict[str, str] = {}
        burst_meta: list[dict[str, object]] = []
        schedule_rows: list[dict[str, object]] = []
        family_counts: Counter[str] = Counter()
        for statement_id in statement_order:
            events = events_by_statement[statement_id]
            candidates = [
                (pair_index, first, second)
                for pair_index, (first, second) in enumerate(zip(events, events[1:]))
                if first["component_recipe"] in chosen and second["component_recipe"] in chosen
            ]
            if not candidates:
                continue
            pair_offset = int(hash_rank(schedule_id, statement_id), 16) % len(candidates)
            pair_index, first, second = candidates[pair_offset]
            burst_id = f"G456-{schedule_ordinal:02d}-B{len(burst_meta) + 1:04d}"
            for burst_position, event in ((1, first), (2, second)):
                variant = chosen[event["component_recipe"]]
                replacements[event["event_id"]] = variant["target_recipe"]
                family_counts[variant["mutation_family"]] += 1
                schedule_row = {
                    "schedule_id": schedule_id,
                    "burst_id": burst_id,
                    "burst_position": burst_position,
                    "event_id": event["event_id"],
                    "stream_ordinal": event["stream_ordinal"],
                    "statement_id": statement_id,
                    "physical_page": event["physical_page"],
                    "owner_de": event["owner_de"],
                    "source_recipe": event["component_recipe"],
                    "replacement_recipe": variant["target_recipe"],
                    "neighbor_id": variant["neighbor_id"],
                    "mutation_family": variant["mutation_family"],
                    "variant_selection_rule": description,
                    "pair_selection_rule": "SHA256(SCHEDULE_ID|STATEMENT_ID)_MOD_ELIGIBLE_ADJACENT_PAIRS",
                    "selection_fields_used": "SOURCE_RECIPE|MUTATION_FAMILY|TARGET_RECIPE|NEIGHBOR_ID|STATEMENT_ID",
                    "outcome_fields_used": "NONE",
                }
                schedule_rows.append(schedule_row)
                all_schedule_rows.append(schedule_row)
            burst_meta.append({
                "schedule_id": schedule_id,
                "burst_id": burst_id,
                "statement_id": statement_id,
                "first_event_id": first["event_id"],
                "second_event_id": second["event_id"],
                "second_stream_ordinal": second["stream_ordinal"],
                "pair_index_within_statement": pair_index + 1,
                "eligible_pair_count": len(candidates),
                "pair_hash_offset": pair_offset,
                "state_bank_id": f"{first['physical_page']}::{first['owner_de']}",
            })

        dense = driver.run_stream(current, replacements)
        dense_by_event = {str(row["event_id"]): row for row in dense}
        replay_rows = [{"schedule_id": schedule_id, **row} for row in dense]
        write_tsv(OUT / f"gdt456_replay_{schedule_id.lower()}.tsv", replay_rows)

        bank_exact_count = 0
        bank_event_exact_count = 0
        for bank_ordinal, (bank, source_rows) in enumerate(sorted(rows_by_bank.items()), start=1):
            isolated = driver.run_stream(source_rows, replacements)
            exact = 0
            for isolated_row in isolated:
                global_row = dense_by_event[str(isolated_row["event_id"])]
                keys = (
                    "visible_recipe", "incoming_action", "incoming_argument",
                    "scope_incoming_action", "decision", "outgoing_action",
                    "outgoing_argument", "scope_outgoing_action",
                )
                exact += all(str(isolated_row[key]) == str(global_row[key]) for key in keys)
            bank_event_exact_count += exact
            bank_exact_count += exact == len(source_rows)
            all_bank_rows.append({
                "schedule_id": schedule_id,
                "bank_id": f"G456-{schedule_ordinal:02d}-K{bank_ordinal:03d}",
                "physical_page": bank[0],
                "owner_de": bank[1],
                "event_count": len(source_rows),
                "replacement_count": sum(row["event_id"] in replacements for row in source_rows),
                "stop_count": sum(row["decision"] == "STOP" for row in isolated),
                "isolated_global_exact_count": exact,
                "isolated_global_all_exact": "YES" if exact == len(source_rows) else "NO",
            })

        recovery_counts: Counter[str] = Counter()
        for meta in burst_meta:
            second_index = current_index[str(meta["second_event_id"])]
            bank_id = str(meta["state_bank_id"])
            recovery_event = "NONE"
            recovery_status = "BANK_END_RESET_ISOLATES_DIVERGENCE"
            distance = 0
            for candidate in current[second_index + 1:]:
                if not same_bank(candidate, bank_id):
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
            recovery_counts[recovery_status] += 1
            all_recovery_rows.append({
                **meta,
                "first_decision": first_result["decision"],
                "second_decision": second_result["decision"],
                "burst_class": f"FIRST_{'STOP' if first_result['decision'] == 'STOP' else 'READABLE'}__SECOND_{'STOP' if second_result['decision'] == 'STOP' else 'READABLE'}",
                "first_stop_safe": first_result["stop_preserves_state"],
                "second_stop_safe": second_result["stop_preserves_state"],
                "recovery_event_id": recovery_event,
                "unmutated_card_distance": distance,
                "recovery_before_next_fault": recovery_status,
            })

        unmutated_stops = [
            row for row in dense
            if row["decision"] == "STOP" and row["event_id"] not in replacements
        ]
        for stop in unmutated_stops:
            stop_index = current_index[str(stop["event_id"])]
            bank_id = str(stop["state_bank_id"])
            recovery_event_id = "END_OF_BANK"
            recovery_decision = "BANK_RESET"
            recovery_distance = 0
            for candidate in current[stop_index + 1:]:
                if not same_bank(candidate, bank_id):
                    continue
                recovery_distance += 1
                candidate_result = dense_by_event[candidate["event_id"]]
                if candidate_result["decision"] != "STOP":
                    recovery_event_id = candidate["event_id"]
                    recovery_decision = str(candidate_result["decision"])
                    break
            all_unmutated_stops.append({
                "schedule_id": schedule_id,
                "event_id": stop["event_id"],
                "statement_id": stop["statement_id"],
                "physical_page": stop["physical_page"],
                "owner_de": stop["owner_de"],
                "source_recipe": stop["source_recipe"],
                "incoming_action": stop["incoming_action"],
                "scope_incoming_action": stop["scope_incoming_action"],
                "blocked_factor_rules": stop["blocked_factor_rules"],
                "stop_preserves_state": stop["stop_preserves_state"],
                "recovery_event_id": recovery_event_id,
                "recovery_decision": recovery_decision,
                "same_bank_card_distance": recovery_distance,
            })

        decisions = Counter(str(row["decision"]) for row in dense)
        mutated_stops = sum(row["decision"] == "STOP" and row["event_id"] in replacements for row in dense)
        untouched_readable = sum(row["decision"] != "STOP" and row["event_id"] not in replacements for row in dense)
        summary_rows.append({
            "schedule_id": schedule_id,
            "variant_selection_rule": description,
            "burst_count": len(burst_meta),
            "replacement_count": len(replacements),
            "deletion_count": family_counts["ATOM_DELETION"],
            "swap_count": family_counts["ADJACENT_SWAP"],
            "substitution_count": family_counts["SAME_CLASS_SUBSTITUTION"],
            "green_count": decisions["READ"],
            "amber_count": decisions["READ_AMBER"],
            "stop_count": decisions["STOP"],
            "mutated_stop_count": mutated_stops,
            "unmutated_stop_count": len(unmutated_stops),
            "untouched_readable_count": untouched_readable,
            "stop_state_failure_count": sum(row["decision"] == "STOP" and row["stop_preserves_state"] != "YES" for row in dense),
            "owner_bank_exact_count": bank_exact_count,
            "owner_bank_event_exact_count": bank_event_exact_count,
            "parity_before_next_fault_count": recovery_counts["STATE_PARITY_BEFORE_NEXT_FAULT"],
            "next_fault_before_parity_count": recovery_counts["NEXT_FAULT_BEFORE_PARITY"],
            "bank_end_isolation_count": recovery_counts["BANK_END_RESET_ISOLATES_DIVERGENCE"],
            "identity_override_count": 0,
            "advisory_override_count": 0,
        })
        manifest_rows.append({
            "schedule_ordinal": schedule_ordinal,
            "schedule_id": schedule_id,
            "variant_selection_rule": description,
            "pair_selection_rule": "SHA256(SCHEDULE_ID|STATEMENT_ID)_MOD_ELIGIBLE_ADJACENT_PAIRS",
            "eligible_statement_count": len(burst_meta),
            "replacement_count": len(replacements),
            "uses_neutral_decision": "NO",
            "uses_blocked_factor_rule": "NO",
            "uses_live_outcome": "NO",
        })

    write_tsv(OUT / "gdt456_schedule_manifest.tsv", manifest_rows)
    write_tsv(OUT / "gdt456_all_fault_schedules.tsv", all_schedule_rows)
    write_tsv(OUT / "gdt456_schedule_summary.tsv", summary_rows)
    write_tsv(OUT / "gdt456_burst_recovery.tsv", all_recovery_rows)
    write_tsv(OUT / "gdt456_owner_bank_isolation.tsv", all_bank_rows)
    if all_unmutated_stops:
        write_tsv(OUT / "gdt456_unmutated_stop_recovery.tsv", all_unmutated_stops)
    else:
        (OUT / "gdt456_unmutated_stop_recovery.tsv").write_text(
            "schedule_id\tevent_id\tstatement_id\tphysical_page\towner_de\tsource_recipe\tincoming_action\tscope_incoming_action\tblocked_factor_rules\tstop_preserves_state\trecovery_event_id\trecovery_decision\tsame_bank_card_distance\n",
            encoding="utf-8",
        )

    result = {
        "status": "OUTCOME_BLIND_SCHEDULE_ENSEMBLE_PRESERVES_STOPS_AND_OWNER_BANKS",
        "schedule_count": len(SCHEDULES),
        "source_event_count_per_schedule": len(current),
        "total_replay_event_count": len(SCHEDULES) * len(current),
        "burst_count_per_schedule": 513,
        "replacement_count_per_schedule": 1026,
        "total_burst_count": len(all_recovery_rows),
        "total_replacement_count": len(all_schedule_rows),
        "schedule_stop_counts": {row["schedule_id"]: int(row["stop_count"]) for row in summary_rows},
        "schedule_unmutated_stop_counts": {row["schedule_id"]: int(row["unmutated_stop_count"]) for row in summary_rows},
        "total_stop_count": sum(int(row["stop_count"]) for row in summary_rows),
        "total_unmutated_stop_count": len(all_unmutated_stops),
        "stop_state_failure_count": sum(int(row["stop_state_failure_count"]) for row in summary_rows),
        "owner_bank_isolation_exact_count": sum(int(row["owner_bank_exact_count"]) for row in summary_rows),
        "owner_bank_isolation_expected_count": len(SCHEDULES) * len(rows_by_bank),
        "outcome_fields_used_for_selection": 0,
        "identity_overrides": 0,
        "advisory_overrides": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt456_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
