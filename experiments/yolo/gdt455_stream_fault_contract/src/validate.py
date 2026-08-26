#!/usr/bin/env python3
"""Validate the dense full-stream fault contract and its fixed schedule."""

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
BASE = ROOT / "experiments/yolo/gdt455_stream_fault_contract"
OUT = BASE / "artifacts"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
VARIANTS = ROOT / "experiments/yolo/gdt454_two_card_neighbor_burst_stress/artifacts/gdt454_selected_neighbor_variants.tsv"
RUN_PATH = BASE / "src/run.py"
DRIVER_PATH = BASE / "src/stream_fault_driver.py"
VALIDATION = OUT / "gdt455_validation.json"
DETERMINISTIC_OUTPUTS = [
    OUT / "gdt455_dense_fault_schedule.tsv",
    OUT / "gdt455_dense_stream_replay.tsv",
    OUT / "gdt455_owner_bank_isolation.tsv",
    OUT / "gdt455_burst_recovery.tsv",
    OUT / "gdt455_result.json",
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

    current = sorted(read_tsv(CURRENT), key=lambda row: int(row["stream_ordinal"]))
    variants = read_tsv(VARIANTS)
    schedule = read_tsv(OUT / "gdt455_dense_fault_schedule.tsv")
    replay = read_tsv(OUT / "gdt455_dense_stream_replay.tsv")
    banks = read_tsv(OUT / "gdt455_owner_bank_isolation.tsv")
    recovery = read_tsv(OUT / "gdt455_burst_recovery.tsv")
    result = json.loads((OUT / "gdt455_result.json").read_text(encoding="utf-8"))
    driver = load_module("gdt455_validation_driver", DRIVER_PATH)
    run = load_module("gdt455_validation_builder", RUN_PATH)

    check("source_count", len(current) == 4576, f"observed={len(current)}")
    check("source_ordinals", [int(row["stream_ordinal"]) for row in current] == list(range(1, 4577)), "1..4576")
    check("statement_count", len({row["statement_id"] for row in current}) == 715, "expected=715")
    check("schedule_rows", len(schedule) == 1026, f"observed={len(schedule)}")
    check("schedule_bursts", len({row["burst_id"] for row in schedule}) == 513, "expected=513")
    check("replay_count", len(replay) == 4576, f"observed={len(replay)}")
    check("recovery_count", len(recovery) == 513, f"observed={len(recovery)}")
    check("bank_count", len(banks) == 57, f"observed={len(banks)}")

    # Reconstruct the source-wise adversarial variant choice.
    variants_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in variants:
        if row["target_recipe"] != "EMPTY_RECIPE":
            variants_by_source[row["source_recipe"]].append(row)
    best = {source: min(rows, key=run.variant_rank) for source, rows in variants_by_source.items()}
    check("nonempty_variant_coverage", len(best) == 1554, f"sources={len(best)}; nine one-atom sources lack a visible neighbour")
    schedule_by_event = {row["event_id"]: row for row in schedule}
    check("schedule_event_unique", len(schedule_by_event) == len(schedule), "no duplicate event replacement")
    check("scheduled_variant_exact", all(
        row["replacement_recipe"] == best[row["source_recipe"]]["target_recipe"]
        and row["neighbor_id"] == best[row["source_recipe"]]["neighbor_id"]
        for row in schedule
    ), "all replacements use fixed source-wise adversarial minimum")

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in current:
        events_by_statement[row["statement_id"]].append(row)
    schedule_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in schedule:
        schedule_by_statement[row["statement_id"]].append(row)
    multi = {statement for statement, rows in events_by_statement.items() if len(rows) >= 2}
    single = set(events_by_statement) - multi
    eligible_statements = {
        statement for statement, rows in events_by_statement.items()
        if any(
            left["component_recipe"] in best and right["component_recipe"] in best
            for left, right in zip(rows, rows[1:])
        )
    }
    check("one_burst_per_eligible_statement", set(schedule_by_statement) == eligible_statements, f"covered={len(schedule_by_statement)}")
    check("one_ineligible_multi_statement", len(multi - eligible_statements) == 1, str(sorted(multi - eligible_statements)))
    check("no_single_statement_fault", not (set(schedule_by_statement) & single), f"single={len(single)}")
    pair_contract_ok = True
    pair_choice_ok = True
    for statement_id, source_rows in events_by_statement.items():
        if len(source_rows) < 2:
            continue
        if statement_id not in eligible_statements:
            continue
        selected = sorted(schedule_by_statement[statement_id], key=lambda row: int(row["burst_position"]))
        first_index = next(i for i, row in enumerate(source_rows) if row["event_id"] == selected[0]["event_id"])
        pair_contract_ok &= (
            len(selected) == 2
            and selected[0]["burst_position"] == "1"
            and selected[1]["burst_position"] == "2"
            and first_index + 1 < len(source_rows)
            and source_rows[first_index + 1]["event_id"] == selected[1]["event_id"]
            and selected[0]["physical_page"] == selected[1]["physical_page"]
            and selected[0]["owner_de"] == selected[1]["owner_de"]
        )
        scored_pairs = [
            (i, sum(
                best[event["component_recipe"]]["neutral_selection_class"] == "NEUTRAL_STOP"
                for event in pair
            ))
            for i, pair in enumerate(zip(source_rows, source_rows[1:]))
            if all(event["component_recipe"] in best for event in pair)
        ]
        expected_index = max(scored_pairs, key=lambda item: (item[1], -item[0]))[0]
        pair_choice_ok &= first_index == expected_index
    check("adjacent_pair_contract", pair_contract_ok, "two adjacent events inside each statement and owner")
    check("max_stop_earliest_pair", pair_choice_ok, "maximum neutral-stop score, earliest tie")

    baseline = driver.run_stream(current)
    check("baseline_decisions", all(
        row["decision"] == ("READ_AMBER" if source["factor_gate_status"] == "FACTOR_AMBER_LOCAL_APPENDIX" else "READ")
        for row, source in zip(baseline, current)
    ), "4576 authoritative decisions")
    check("baseline_states", all(
        row["incoming_action"] == source["active_action_before"]
        and row["incoming_argument"] == source["active_argument_before"]
        and row["outgoing_action"] == source["active_action_after"]
        and row["outgoing_argument"] == source["active_argument_after"]
        for row, source in zip(baseline, current)
    ), "4576 incoming/outgoing state transitions")

    check("replay_event_order", [row["event_id"] for row in replay] == [row["event_id"] for row in current], "exact source order")
    check("replacement_binding", all(
        row["visible_recipe"] == (
            schedule_by_event[row["event_id"]]["replacement_recipe"]
            if row["event_id"] in schedule_by_event else row["source_recipe"]
        ) for row in replay
    ), "scheduled and untouched recipes exact")
    check("replacement_flags", sum(row["recipe_replaced"] == "YES" for row in replay) == 1026, "expected=1026")
    check("no_empty_visible_recipe", all(row["visible_recipe"] != "EMPTY_RECIPE" for row in replay), "all replacements remain visible nonempty recipes")
    lookahead_ok = True
    for index, row in enumerate(replay):
        expected = "NONE"
        if index + 1 < len(replay):
            next_row = replay[index + 1]
            if (
                next_row["statement_id"] == row["statement_id"]
                and next_row["physical_page"] == row["physical_page"]
                and next_row["owner_de"] == row["owner_de"]
            ):
                expected = next_row["visible_recipe"]
        lookahead_ok &= row["visible_next_recipe"] == expected
    check("visible_one_card_lookahead", lookahead_ok, "never crosses statement/page/owner")

    stops = [row for row in replay if row["decision"] == "STOP"]
    check("dense_decision_counts", Counter(row["decision"] for row in replay) == Counter({"READ": 4234, "READ_AMBER": 20, "STOP": 322}), str(Counter(row["decision"] for row in replay)))
    check("all_stops_state_safe", all(
        row["stop_preserves_state"] == "YES"
        and row["incoming_action"] == row["outgoing_action"]
        and row["incoming_argument"] == row["outgoing_argument"]
        and row["scope_incoming_action"] == row["scope_outgoing_action"]
        for row in stops
    ), f"stops={len(stops)}")
    check("no_other_bank_writes", all(row["other_bank_write_count"] == "0" for row in replay), "all rows")
    check("owner_bank_isolation", all(
        row["isolated_global_all_exact"] == "YES"
        and int(row["isolated_global_exact_count"]) == int(row["event_count"])
        for row in banks
    ), "57/57 isolated bank replays exact")
    check("owner_bank_event_sum", sum(int(row["event_count"]) for row in banks) == 4576, "expected=4576")

    burst_counts = Counter(row["burst_class"] for row in recovery)
    recovery_counts = Counter(row["recovery_before_next_fault"] for row in recovery)
    check("burst_classes", burst_counts == Counter({
        "FIRST_READABLE__SECOND_READABLE": 246,
        "FIRST_READABLE__SECOND_STOP": 126,
        "FIRST_STOP__SECOND_READABLE": 86,
        "FIRST_STOP__SECOND_STOP": 55,
    }), str(burst_counts))
    check("recovery_classes", recovery_counts == Counter({
        "STATE_PARITY_BEFORE_NEXT_FAULT": 383,
        "NEXT_FAULT_BEFORE_PARITY": 123,
        "BANK_END_RESET_ISOLATES_DIVERGENCE": 7,
    }), str(recovery_counts))
    check("bank_end_isolation", all(
        row["post_bank_boundary_is_distinct"] in {"YES", "END_OF_STREAM"}
        and (row["post_bank_boundary_id"] == "END_OF_STREAM" or row["post_bank_boundary_id"] != row["state_bank_id"])
        for row in recovery if row["recovery_before_next_fault"] == "BANK_END_RESET_ISOLATES_DIVERGENCE"
    ), "all seven end at an independent bank or stream end")
    check("burst_stop_flags", all(
        (row["first_decision"] != "STOP" or row["first_stop_safe"] == "YES")
        and (row["second_decision"] != "STOP" or row["second_stop_safe"] == "YES")
        for row in recovery
    ), "all burst-position stops safe")

    check("identity_no_override", all(row["identity_can_override"] == "NO" for row in replay), "4576/4576")
    check("advisory_no_override", all(row["advisory_can_override"] == "NO" for row in replay), "4576/4576")
    check("no_sealed_pages", all(not row["physical_page"].lower().startswith("f84") for row in replay), "fixed current pages only")
    check("claim_ceiling_zeros", all(result[key] == 0 for key in (
        "identity_overrides", "advisory_overrides", "meaning_revisions",
        "surface_predictions", "occurrence_predictions", "new_pages",
    )), "all forbidden promotions zero")
    check("result_counts", (
        result["source_event_count"] == 4576
        and result["scheduled_burst_count"] == 513
        and result["replaced_event_count"] == 1026
        and result["dense_stop_count"] == 322
        and result["owner_bank_isolation_exact_count"] == 57
    ), "compact result matches ledgers")

    before = {path: sha256(path) for path in DETERMINISTIC_OUTPUTS}
    run.main()
    after = {path: sha256(path) for path in DETERMINISTIC_OUTPUTS}
    check("deterministic_rebuild", before == after, "all five generated artifacts byte-identical")
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
