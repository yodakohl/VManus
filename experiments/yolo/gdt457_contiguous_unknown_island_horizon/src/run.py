#!/usr/bin/env python3
"""Measure recovery across matched nested visible fault islands of length 1..16."""

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
BASE = ROOT / "experiments/yolo/gdt457_contiguous_unknown_island_horizon"
OUT = BASE / "artifacts"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
VARIANTS = ROOT / "experiments/yolo/gdt454_two_card_neighbor_burst_stress/artifacts/gdt454_selected_neighbor_variants.tsv"
DRIVER_PATH = ROOT / "experiments/yolo/gdt455_stream_fault_contract/src/stream_fault_driver.py"
MAX_LENGTH = 16


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


def replay_digest(rows: list[dict[str, object]]) -> str:
    fields = (
        "event_id", "visible_recipe", "incoming_action", "incoming_argument",
        "scope_incoming_action", "decision", "blocked_factor_rules",
        "outgoing_action", "outgoing_argument", "scope_outgoing_action",
    )
    payload = "\n".join("\t".join(str(row[field]) for field in fields) for row in rows) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def same_bank(row: dict[str, str], bank_id: str) -> bool:
    return f"{row['physical_page']}::{row['owner_de']}" == bank_id


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    driver = load_module("gdt457_fault_driver", DRIVER_PATH)
    current = sorted(read_tsv(CURRENT), key=lambda row: int(row["stream_ordinal"]))
    current_index = {row["event_id"]: index for index, row in enumerate(current)}
    baseline = driver.run_stream(current)
    baseline_by_event = {str(row["event_id"]): row for row in baseline}

    variants_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(VARIANTS):
        if row["target_recipe"] != "EMPTY_RECIPE":
            variants_by_source[row["source_recipe"]].append(row)
    chosen = {
        source: min(
            rows,
            key=lambda row: (
                hash_rank("GDT457_HASH_MIN", source, row["target_recipe"], row["neighbor_id"]),
                row["target_recipe"], row["neighbor_id"],
            ),
        ) for source, rows in variants_by_source.items()
    }

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    statement_order: list[str] = []
    for event in current:
        if event["statement_id"] not in events_by_statement:
            statement_order.append(event["statement_id"])
        events_by_statement[event["statement_id"]].append(event)
    rows_by_bank: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for event in current:
        rows_by_bank[(event["physical_page"], event["owner_de"])].append(event)

    anchor_rows: list[dict[str, object]] = []
    anchors: list[dict[str, object]] = []
    for statement_id in statement_order:
        events = events_by_statement[statement_id]
        windows = [
            start for start in range(len(events) - MAX_LENGTH + 1)
            if all(event["component_recipe"] in chosen for event in events[start:start + MAX_LENGTH])
        ]
        if not windows:
            continue
        offset = int(hash_rank("GDT457_ANCHOR", statement_id), 16) % len(windows)
        start = windows[offset]
        window = events[start:start + MAX_LENGTH]
        anchor_id = f"G457-A{len(anchors) + 1:03d}"
        anchor = {
            "anchor_id": anchor_id,
            "statement_id": statement_id,
            "physical_page": window[0]["physical_page"],
            "register": window[0]["register"],
            "owner_de": window[0]["owner_de"],
            "state_bank_id": f"{window[0]['physical_page']}::{window[0]['owner_de']}",
            "statement_event_count": len(events),
            "eligible_window_count": len(windows),
            "selected_window_offset": offset,
            "window_start_position": start + 1,
            "first_event_id": window[0]["event_id"],
            "last_event_id": window[-1]["event_id"],
            "window_event_ids": "|".join(event["event_id"] for event in window),
            "window_source_recipes": "|".join(event["component_recipe"] for event in window),
        }
        anchors.append({**anchor, "events": window})
        anchor_rows.append(anchor)
    write_tsv(OUT / "gdt457_matched_16_card_anchors.tsv", anchor_rows)

    schedule_rows: list[dict[str, object]] = []
    island_rows: list[dict[str, object]] = []
    unmutated_stop_rows: list[dict[str, object]] = []
    bank_rows: list[dict[str, object]] = []
    digest_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for length in range(1, MAX_LENGTH + 1):
        length_id = f"L{length:02d}"
        replacements: dict[str, str] = {}
        islands: list[dict[str, object]] = []
        for anchor in anchors:
            window = list(anchor["events"])
            selected = window[:length]
            island_id = f"G457-{length_id}-{anchor['anchor_id']}"
            for position, event in enumerate(selected, start=1):
                variant = chosen[event["component_recipe"]]
                replacements[event["event_id"]] = variant["target_recipe"]
                schedule_rows.append({
                    "length_id": length_id,
                    "island_length": length,
                    "island_id": island_id,
                    "anchor_id": anchor["anchor_id"],
                    "island_position": position,
                    "event_id": event["event_id"],
                    "stream_ordinal": event["stream_ordinal"],
                    "statement_id": event["statement_id"],
                    "physical_page": event["physical_page"],
                    "owner_de": event["owner_de"],
                    "source_recipe": event["component_recipe"],
                    "replacement_recipe": variant["target_recipe"],
                    "neighbor_id": variant["neighbor_id"],
                    "mutation_family": variant["mutation_family"],
                    "variant_selection_rule": "SOURCE_BOUND_SHA256_MIN__NO_OUTCOME_FIELD",
                    "nested_anchor_rule": "PREFIX_OF_FIXED_16_CARD_WINDOW",
                })
            islands.append({
                "length_id": length_id,
                "island_length": length,
                "island_id": island_id,
                "anchor_id": anchor["anchor_id"],
                "statement_id": anchor["statement_id"],
                "state_bank_id": anchor["state_bank_id"],
                "first_event_id": selected[0]["event_id"],
                "last_event_id": selected[-1]["event_id"],
                "last_stream_ordinal": selected[-1]["stream_ordinal"],
            })

        replay = driver.run_stream(current, replacements)
        replay_by_event = {str(row["event_id"]): row for row in replay}
        digest_rows.append({
            "length_id": length_id,
            "island_length": length,
            "event_count": len(replay),
            "replacement_count": len(replacements),
            "canonical_replay_sha256": replay_digest(replay),
        })

        bank_exact = 0
        bank_event_exact = 0
        for bank_ordinal, (bank, source_rows) in enumerate(sorted(rows_by_bank.items()), start=1):
            isolated = driver.run_stream(source_rows, replacements)
            exact = 0
            for isolated_row in isolated:
                global_row = replay_by_event[str(isolated_row["event_id"])]
                fields = (
                    "visible_recipe", "incoming_action", "incoming_argument",
                    "scope_incoming_action", "decision", "outgoing_action",
                    "outgoing_argument", "scope_outgoing_action",
                )
                exact += all(str(isolated_row[field]) == str(global_row[field]) for field in fields)
            bank_event_exact += exact
            bank_exact += exact == len(source_rows)
            bank_rows.append({
                "length_id": length_id,
                "island_length": length,
                "bank_id": f"G457-{length_id}-K{bank_ordinal:03d}",
                "physical_page": bank[0],
                "owner_de": bank[1],
                "event_count": len(source_rows),
                "replacement_count": sum(row["event_id"] in replacements for row in source_rows),
                "stop_count": sum(row["decision"] == "STOP" for row in isolated),
                "isolated_global_exact_count": exact,
                "isolated_global_all_exact": "YES" if exact == len(source_rows) else "NO",
            })

        recovery_counts: Counter[str] = Counter()
        immediate_counts: Counter[str] = Counter()
        for island in islands:
            last_index = current_index[str(island["last_event_id"])]
            bank_id = str(island["state_bank_id"])
            immediate_event = None
            if last_index + 1 < len(current):
                candidate = current[last_index + 1]
                if candidate["statement_id"] == island["statement_id"] and same_bank(candidate, bank_id):
                    immediate_event = candidate
            immediate_decision = (
                str(replay_by_event[immediate_event["event_id"]]["decision"])
                if immediate_event else "NO_SAME_STATEMENT_CARD"
            )
            immediate_counts[immediate_decision] += 1

            state_status = "BANK_END_RESET_ISOLATES_DIVERGENCE"
            state_event = "NONE"
            state_distance = 0
            for candidate in current[last_index + 1:]:
                if not same_bank(candidate, bank_id):
                    continue
                if candidate["event_id"] in replacements:
                    state_status = "NEXT_ISLAND_BEFORE_PARITY"
                    state_event = candidate["event_id"]
                    break
                state_distance += 1
                actual = replay_by_event[candidate["event_id"]]
                reference = baseline_by_event[candidate["event_id"]]
                if actual["outgoing_action"] == reference["outgoing_action"] and actual["outgoing_argument"] == reference["outgoing_argument"]:
                    state_status = "STATE_PARITY_BEFORE_NEXT_ISLAND"
                    state_event = candidate["event_id"]
                    break
            recovery_counts[state_status] += 1

            cascade_count = 0
            cascade_recovery_event = "NO_SAME_STATEMENT_CARD"
            cascade_recovery_decision = "NOT_APPLICABLE"
            for candidate in current[last_index + 1:]:
                if candidate["statement_id"] != island["statement_id"] or not same_bank(candidate, bank_id):
                    break
                result = replay_by_event[candidate["event_id"]]
                if result["decision"] == "STOP":
                    cascade_count += 1
                    continue
                cascade_recovery_event = candidate["event_id"]
                cascade_recovery_decision = str(result["decision"])
                break
            island_rows.append({
                **island,
                "immediate_post_island_event_id": immediate_event["event_id"] if immediate_event else "NONE",
                "immediate_post_island_decision": immediate_decision,
                "untouched_stop_cascade_length": cascade_count,
                "cascade_recovery_event_id": cascade_recovery_event,
                "cascade_recovery_decision": cascade_recovery_decision,
                "state_recovery_event_id": state_event,
                "unmutated_card_distance_to_parity_or_next_island": state_distance,
                "state_recovery_status": state_status,
            })

        unmutated_stops = [
            row for row in replay
            if row["decision"] == "STOP" and row["event_id"] not in replacements
        ]
        for stop in unmutated_stops:
            stop_index = current_index[str(stop["event_id"])]
            bank_id = str(stop["state_bank_id"])
            recovery_event = "END_OF_BANK"
            recovery_decision = "BANK_RESET"
            distance = 0
            for candidate in current[stop_index + 1:]:
                if not same_bank(candidate, bank_id):
                    continue
                distance += 1
                candidate_result = replay_by_event[candidate["event_id"]]
                if candidate_result["decision"] != "STOP":
                    recovery_event = candidate["event_id"]
                    recovery_decision = str(candidate_result["decision"])
                    break
            unmutated_stop_rows.append({
                "length_id": length_id,
                "island_length": length,
                "event_id": stop["event_id"],
                "statement_id": stop["statement_id"],
                "physical_page": stop["physical_page"],
                "owner_de": stop["owner_de"],
                "source_recipe": stop["source_recipe"],
                "incoming_action": stop["incoming_action"],
                "scope_incoming_action": stop["scope_incoming_action"],
                "blocked_factor_rules": stop["blocked_factor_rules"],
                "stop_preserves_state": stop["stop_preserves_state"],
                "recovery_event_id": recovery_event,
                "recovery_decision": recovery_decision,
                "same_bank_card_distance": distance,
            })

        decisions = Counter(str(row["decision"]) for row in replay)
        summary_rows.append({
            "length_id": length_id,
            "island_length": length,
            "matched_anchor_count": len(anchors),
            "replacement_count": len(replacements),
            "replacement_density": f"{len(replacements) / len(current):.6f}",
            "green_count": decisions["READ"],
            "amber_count": decisions["READ_AMBER"],
            "stop_count": decisions["STOP"],
            "mutated_stop_count": sum(row["decision"] == "STOP" and row["event_id"] in replacements for row in replay),
            "unmutated_stop_count": len(unmutated_stops),
            "immediate_post_island_readable_count": immediate_counts["READ"] + immediate_counts["READ_AMBER"],
            "immediate_post_island_stop_count": immediate_counts["STOP"],
            "no_same_statement_post_card_count": immediate_counts["NO_SAME_STATEMENT_CARD"],
            "max_untouched_stop_cascade": max(row["untouched_stop_cascade_length"] for row in island_rows if row["length_id"] == length_id),
            "parity_before_next_island_count": recovery_counts["STATE_PARITY_BEFORE_NEXT_ISLAND"],
            "next_island_before_parity_count": recovery_counts["NEXT_ISLAND_BEFORE_PARITY"],
            "bank_end_isolation_count": recovery_counts["BANK_END_RESET_ISOLATES_DIVERGENCE"],
            "stop_state_failure_count": sum(row["decision"] == "STOP" and row["stop_preserves_state"] != "YES" for row in replay),
            "owner_bank_exact_count": bank_exact,
            "owner_bank_event_exact_count": bank_event_exact,
        })

    write_tsv(OUT / "gdt457_nested_fault_schedule.tsv", schedule_rows)
    write_tsv(OUT / "gdt457_island_recovery.tsv", island_rows)
    write_tsv(OUT / "gdt457_owner_bank_isolation.tsv", bank_rows)
    write_tsv(OUT / "gdt457_stream_digests.tsv", digest_rows)
    write_tsv(OUT / "gdt457_length_summary.tsv", summary_rows)
    if unmutated_stop_rows:
        write_tsv(OUT / "gdt457_unmutated_stop_recovery.tsv", unmutated_stop_rows)
    else:
        (OUT / "gdt457_unmutated_stop_recovery.tsv").write_text(
            "length_id\tisland_length\tevent_id\tstatement_id\tphysical_page\towner_de\tsource_recipe\tincoming_action\tscope_incoming_action\tblocked_factor_rules\tstop_preserves_state\trecovery_event_id\trecovery_decision\tsame_bank_card_distance\n",
            encoding="utf-8",
        )

    result = {
        "status": "MATCHED_UNKNOWN_ISLAND_HORIZON_COMPLETE",
        "tested_lengths": list(range(1, MAX_LENGTH + 1)),
        "matched_anchor_count": len(anchors),
        "stream_event_count_per_length": len(current),
        "total_replay_event_count": MAX_LENGTH * len(current),
        "total_island_count": len(island_rows),
        "total_replacement_count": len(schedule_rows),
        "length_stop_counts": {row["length_id"]: int(row["stop_count"]) for row in summary_rows},
        "length_unmutated_stop_counts": {row["length_id"]: int(row["unmutated_stop_count"]) for row in summary_rows},
        "total_stop_count": sum(int(row["stop_count"]) for row in summary_rows),
        "total_unmutated_stop_count": len(unmutated_stop_rows),
        "maximum_untouched_stop_cascade": max(int(row["max_untouched_stop_cascade"]) for row in summary_rows),
        "stop_state_failure_count": sum(int(row["stop_state_failure_count"]) for row in summary_rows),
        "owner_bank_isolation_exact_count": sum(int(row["owner_bank_exact_count"]) for row in summary_rows),
        "owner_bank_isolation_expected_count": MAX_LENGTH * len(rows_by_bank),
        "outcome_fields_used_for_selection": 0,
        "identity_overrides": 0,
        "advisory_overrides": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt457_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
