#!/usr/bin/env python3
"""Validate the matched nested 1..16-card unknown-island horizon."""

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
RUN_PATH = BASE / "src/run.py"
VALIDATION = OUT / "gdt457_validation.json"
DETERMINISTIC_OUTPUTS = [
    OUT / "gdt457_matched_16_card_anchors.tsv",
    OUT / "gdt457_nested_fault_schedule.tsv",
    OUT / "gdt457_island_recovery.tsv",
    OUT / "gdt457_owner_bank_isolation.tsv",
    OUT / "gdt457_stream_digests.tsv",
    OUT / "gdt457_length_summary.tsv",
    OUT / "gdt457_unmutated_stop_recovery.tsv",
    OUT / "gdt457_result.json",
]


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    run = load_module("gdt457_validation_builder", RUN_PATH)
    driver = load_module("gdt457_validation_driver", DRIVER_PATH)
    current = sorted(read_tsv(CURRENT), key=lambda row: int(row["stream_ordinal"]))
    anchors = read_tsv(OUT / "gdt457_matched_16_card_anchors.tsv")
    schedule = read_tsv(OUT / "gdt457_nested_fault_schedule.tsv")
    islands = read_tsv(OUT / "gdt457_island_recovery.tsv")
    banks = read_tsv(OUT / "gdt457_owner_bank_isolation.tsv")
    digests = read_tsv(OUT / "gdt457_stream_digests.tsv")
    summaries = read_tsv(OUT / "gdt457_length_summary.tsv")
    unmutated_stops = read_tsv(OUT / "gdt457_unmutated_stop_recovery.tsv")
    result = json.loads((OUT / "gdt457_result.json").read_text(encoding="utf-8"))

    check("source_count", len(current) == 4576, f"observed={len(current)}")
    check("anchor_count", len(anchors) == 55, f"observed={len(anchors)}")
    check("length_count", [int(row["island_length"]) for row in summaries] == list(range(1, 17)), "1..16")
    check("schedule_count", len(schedule) == 7480, f"observed={len(schedule)}")
    check("island_count", len(islands) == 880, f"observed={len(islands)}")
    check("bank_count", len(banks) == 912, f"observed={len(banks)}")
    check("digest_count", len(digests) == 16, f"observed={len(digests)}")
    check("unmutated_stop_table_empty", len(unmutated_stops) == 0, "header only")

    variants_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(VARIANTS):
        if row["target_recipe"] != "EMPTY_RECIPE":
            variants_by_source[row["source_recipe"]].append(row)
    chosen = {
        source: min(
            rows,
            key=lambda row: (
                run.hash_rank("GDT457_HASH_MIN", source, row["target_recipe"], row["neighbor_id"]),
                row["target_recipe"], row["neighbor_id"],
            ),
        ) for source, rows in variants_by_source.items()
    }
    current_by_event = {row["event_id"]: row for row in current}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in current:
        events_by_statement[row["statement_id"]].append(row)

    anchor_contract = True
    for anchor in anchors:
        events = events_by_statement[anchor["statement_id"]]
        windows = [
            start for start in range(len(events) - 15)
            if all(event["component_recipe"] in chosen for event in events[start:start + 16])
        ]
        expected_offset = int(run.hash_rank("GDT457_ANCHOR", anchor["statement_id"]), 16) % len(windows)
        start = windows[expected_offset]
        expected = events[start:start + 16]
        anchor_contract &= (
            int(anchor["eligible_window_count"]) == len(windows)
            and int(anchor["selected_window_offset"]) == expected_offset
            and int(anchor["window_start_position"]) == start + 1
            and anchor["window_event_ids"] == "|".join(event["event_id"] for event in expected)
            and anchor["window_source_recipes"] == "|".join(event["component_recipe"] for event in expected)
        )
    check("matched_anchor_contract", anchor_contract, "55 fixed 16-card windows")
    check("anchor_register_coverage", set(row["register"] for row in anchors) == {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}, "all five running registers")

    schedule_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in schedule:
        schedule_by_key[(row["length_id"], row["anchor_id"])].append(row)
    schedule_contract = True
    for anchor in anchors:
        anchor_events = anchor["window_event_ids"].split("|")
        for length in range(1, 17):
            length_id = f"L{length:02d}"
            rows = sorted(schedule_by_key[(length_id, anchor["anchor_id"])], key=lambda row: int(row["island_position"]))
            schedule_contract &= (
                len(rows) == length
                and [row["event_id"] for row in rows] == anchor_events[:length]
                and [int(row["island_position"]) for row in rows] == list(range(1, length + 1))
                and all(
                    row["replacement_recipe"] == chosen[row["source_recipe"]]["target_recipe"]
                    and row["neighbor_id"] == chosen[row["source_recipe"]]["neighbor_id"]
                    and row["replacement_recipe"] != "EMPTY_RECIPE"
                    for row in rows
                )
            )
    check("nested_prefix_schedule", schedule_contract, "same 55 anchors; strict prefixes 1..16")
    check("schedule_outcome_blind", all(row["variant_selection_rule"] == "SOURCE_BOUND_SHA256_MIN__NO_OUTCOME_FIELD" for row in schedule), "7480/7480")

    baseline = driver.run_stream(current)
    check("baseline_roundtrip", all(
        row["incoming_action"] == source["active_action_before"]
        and row["incoming_argument"] == source["active_argument_before"]
        and row["outgoing_action"] == source["active_action_after"]
        and row["outgoing_argument"] == source["active_argument_after"]
        for row, source in zip(baseline, current)
    ), "4576/4576")

    expected_stops = [5, 7, 7, 9, 13, 13, 16, 17, 19, 19, 19, 20, 23, 26, 31, 32]
    check("stop_curve", [int(row["stop_count"]) for row in summaries] == expected_stops, str(expected_stops))
    replay_contract = True
    all_stop_safe = True
    no_untouched_stops = True
    digest_contract = True
    schedule_by_length = {
        f"L{length:02d}": {
            row["event_id"]: row["replacement_recipe"]
            for row in schedule if int(row["island_length"]) == length
        } for length in range(1, 17)
    }
    digest_by_length = {row["length_id"]: row for row in digests}
    for length in range(1, 17):
        length_id = f"L{length:02d}"
        replacements = schedule_by_length[length_id]
        replay = driver.run_stream(current, replacements)
        summary = summaries[length - 1]
        decisions = Counter(str(row["decision"]) for row in replay)
        replay_contract &= (
            len(replay) == 4576
            and len(replacements) == 55 * length
            and decisions["READ"] == int(summary["green_count"])
            and decisions["READ_AMBER"] == int(summary["amber_count"])
            and decisions["STOP"] == int(summary["stop_count"])
        )
        digest_contract &= run.replay_digest(replay) == digest_by_length[length_id]["canonical_replay_sha256"]
        for row in replay:
            if row["decision"] == "STOP":
                all_stop_safe &= (
                    row["stop_preserves_state"] == "YES"
                    and row["incoming_action"] == row["outgoing_action"]
                    and row["incoming_argument"] == row["outgoing_argument"]
                    and row["scope_incoming_action"] == row["scope_outgoing_action"]
                )
                no_untouched_stops &= row["event_id"] in replacements
    check("sixteen_stream_replays", replay_contract, "73216 event decisions summarized")
    check("stream_digests", digest_contract, "16 canonical SHA-256 replays")
    check("all_stop_state_safe", all_stop_safe, "276/276")
    check("no_untouched_stops", no_untouched_stops, "all 276 stops inside the fault islands")

    check("immediate_followers", all(
        int(row["immediate_post_island_stop_count"]) == 0
        and int(row["immediate_post_island_readable_count"]) + int(row["no_same_statement_post_card_count"]) == 55
        for row in summaries
    ), "every available immediate untouched follower reads")
    check("zero_stop_cascade", all(row["max_untouched_stop_cascade"] == "0" for row in summaries), "lengths 1..16")
    check("island_recovery_total", Counter(row["state_recovery_status"] for row in islands) == Counter({
        "STATE_PARITY_BEFORE_NEXT_ISLAND": 869,
        "NEXT_ISLAND_BEFORE_PARITY": 5,
        "BANK_END_RESET_ISOLATES_DIVERGENCE": 6,
    }), str(Counter(row["state_recovery_status"] for row in islands)))
    check("owner_bank_isolation", all(
        row["isolated_global_all_exact"] == "YES"
        and row["isolated_global_exact_count"] == row["event_count"]
        for row in banks
    ), "912/912")
    check("owner_bank_event_sum", sum(int(row["event_count"]) for row in banks) == 73216, "16 times 4576")
    check("no_sealed_pages", all(not row["physical_page"].lower().startswith("f84") for row in anchors), "fixed current pages only")
    check("result_counts", (
        result["matched_anchor_count"] == 55
        and result["total_replay_event_count"] == 73216
        and result["total_island_count"] == 880
        and result["total_replacement_count"] == 7480
        and result["total_stop_count"] == 276
        and result["total_unmutated_stop_count"] == 0
        and result["owner_bank_isolation_exact_count"] == 912
    ), "compact result matches all ledgers")
    check("claim_ceiling_zeros", all(result[key] == 0 for key in (
        "outcome_fields_used_for_selection", "identity_overrides", "advisory_overrides",
        "meaning_revisions", "surface_predictions", "occurrence_predictions", "new_pages",
    )), "no forbidden promotions")

    before = {path: sha256(path) for path in DETERMINISTIC_OUTPUTS}
    run.main()
    after = {path: sha256(path) for path in DETERMINISTIC_OUTPUTS}
    check("deterministic_rebuild", before == after, "all eight generated artifacts byte-identical")
    check("artifact_size_limit", all(path.stat().st_size <= 5_000_000 for path in DETERMINISTIC_OUTPUTS), "all generated files <=5MB")

    failures = [row for row in checks if not row["pass"]]
    payload = {
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failures),
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "check_count", "failure_count")}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
