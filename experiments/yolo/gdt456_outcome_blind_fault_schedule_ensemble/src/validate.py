#!/usr/bin/env python3
"""Validate all six outcome-blind full-stream fault schedules."""

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
RUN_PATH = BASE / "src/run.py"
VALIDATION = OUT / "gdt456_validation.json"
REPLAY_PATHS = {
    schedule_id: OUT / f"gdt456_replay_{schedule_id.lower()}.tsv"
    for schedule_id in ("LEX_FIRST", "LEX_LAST", "HASH_MIN", "DELETION_FIRST", "SWAP_FIRST", "SUBSTITUTION_FIRST")
}
DETERMINISTIC_OUTPUTS = [
    OUT / "gdt456_schedule_manifest.tsv",
    OUT / "gdt456_all_fault_schedules.tsv",
    OUT / "gdt456_schedule_summary.tsv",
    OUT / "gdt456_burst_recovery.tsv",
    OUT / "gdt456_owner_bank_isolation.tsv",
    OUT / "gdt456_unmutated_stop_recovery.tsv",
    *REPLAY_PATHS.values(),
    OUT / "gdt456_result.json",
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

    run = load_module("gdt456_validator_builder", RUN_PATH)
    driver = load_module("gdt456_validator_driver", DRIVER_PATH)
    current = sorted(read_tsv(CURRENT), key=lambda row: int(row["stream_ordinal"]))
    variants = read_tsv(VARIANTS)
    manifest = read_tsv(OUT / "gdt456_schedule_manifest.tsv")
    schedules = read_tsv(OUT / "gdt456_all_fault_schedules.tsv")
    summaries = read_tsv(OUT / "gdt456_schedule_summary.tsv")
    recoveries = read_tsv(OUT / "gdt456_burst_recovery.tsv")
    banks = read_tsv(OUT / "gdt456_owner_bank_isolation.tsv")
    unmutated_stops = read_tsv(OUT / "gdt456_unmutated_stop_recovery.tsv")
    result = json.loads((OUT / "gdt456_result.json").read_text(encoding="utf-8"))

    schedule_ids = [row[0] for row in run.SCHEDULES]
    check("schedule_manifest", [row["schedule_id"] for row in manifest] == schedule_ids, str(schedule_ids))
    check("schedule_count", len(schedule_ids) == 6 and len(summaries) == 6, "six fixed schedules")
    check("source_count", len(current) == 4576, f"observed={len(current)}")
    check("schedule_row_count", len(schedules) == 6156, f"observed={len(schedules)}")
    check("burst_recovery_count", len(recoveries) == 3078, f"observed={len(recoveries)}")
    check("bank_row_count", len(banks) == 342, f"observed={len(banks)}")

    variants_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in variants:
        if row["target_recipe"] != "EMPTY_RECIPE":
            variants_by_source[row["source_recipe"]].append(row)
    chosen_by_schedule = {
        schedule_id: {
            source: run.select_variant(schedule_id, source, rows)
            for source, rows in variants_by_source.items()
        }
        for schedule_id in schedule_ids
    }
    check("nonempty_variant_pool", len(variants_by_source) == 1554, "nine one-atom sources excluded")
    check("selection_declares_no_outcomes", all(
        row["outcome_fields_used"] == "NONE"
        and row["selection_fields_used"] == "SOURCE_RECIPE|MUTATION_FAMILY|TARGET_RECIPE|NEIGHBOR_ID|STATEMENT_ID"
        for row in schedules
    ), "6156/6156")
    check("variant_selection_reproduces", all(
        row["replacement_recipe"] == chosen_by_schedule[row["schedule_id"]][row["source_recipe"]]["target_recipe"]
        and row["neighbor_id"] == chosen_by_schedule[row["schedule_id"]][row["source_recipe"]]["neighbor_id"]
        for row in schedules
    ), "selection ignores neutral decision and blocked-rule columns")
    check("no_empty_replacement", all(row["replacement_recipe"] != "EMPTY_RECIPE" for row in schedules), "visible recipes only")

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in current:
        events_by_statement[row["statement_id"]].append(row)
    schedules_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in schedules:
        schedules_by_key[(row["schedule_id"], row["statement_id"])].append(row)
    pair_contract = True
    pair_hash_exact = True
    for schedule_id in schedule_ids:
        chosen = chosen_by_schedule[schedule_id]
        for statement_id, events in events_by_statement.items():
            candidates = [
                (i, left, right)
                for i, (left, right) in enumerate(zip(events, events[1:]))
                if left["component_recipe"] in chosen and right["component_recipe"] in chosen
            ]
            selected = sorted(schedules_by_key.get((schedule_id, statement_id), []), key=lambda row: int(row["burst_position"]))
            if not candidates:
                pair_contract &= not selected
                continue
            pair_contract &= len(selected) == 2
            offset = int(run.hash_rank(schedule_id, statement_id), 16) % len(candidates)
            expected_index, expected_first, expected_second = candidates[offset]
            pair_hash_exact &= (
                selected[0]["event_id"] == expected_first["event_id"]
                and selected[1]["event_id"] == expected_second["event_id"]
                and int(selected[0]["burst_position"]) == 1
                and int(selected[1]["burst_position"]) == 2
                and int(selected[0]["stream_ordinal"]) + 1 == int(selected[1]["stream_ordinal"])
                and selected[0]["statement_id"] == selected[1]["statement_id"]
                and selected[0]["owner_de"] == selected[1]["owner_de"]
                and expected_index + 1 == int(next(row["pair_index_within_statement"] for row in recoveries if row["burst_id"] == selected[0]["burst_id"]))
            )
    check("one_pair_per_eligible_statement", pair_contract, "513 per schedule; one ineligible statement")
    check("pair_hash_reproduces", pair_hash_exact, "outcome-blind hashed pair position")

    baseline = driver.run_stream(current)
    check("baseline_roundtrip", all(
        row["incoming_action"] == source["active_action_before"]
        and row["incoming_argument"] == source["active_argument_before"]
        and row["outgoing_action"] == source["active_action_after"]
        and row["outgoing_argument"] == source["active_argument_after"]
        for row, source in zip(baseline, current)
    ), "4576/4576")

    expected_decisions = {
        "LEX_FIRST": Counter({"READ": 4518, "READ_AMBER": 20, "STOP": 38}),
        "LEX_LAST": Counter({"READ": 4519, "READ_AMBER": 16, "STOP": 41}),
        "HASH_MIN": Counter({"READ": 4512, "READ_AMBER": 20, "STOP": 44}),
        "DELETION_FIRST": Counter({"READ": 4554, "READ_AMBER": 18, "STOP": 4}),
        "SWAP_FIRST": Counter({"READ": 4500, "READ_AMBER": 26, "STOP": 50}),
        "SUBSTITUTION_FIRST": Counter({"READ": 4521, "READ_AMBER": 19, "STOP": 36}),
    }
    all_replay_rows: list[dict[str, str]] = []
    schedule_by_event = {
        schedule_id: {
            row["event_id"]: row["replacement_recipe"]
            for row in schedules if row["schedule_id"] == schedule_id
        }
        for schedule_id in schedule_ids
    }
    replay_contract = True
    lookahead_contract = True
    stop_safety = True
    untouched_stop_counter: Counter[tuple[str, str]] = Counter()
    for schedule_id in schedule_ids:
        replay = read_tsv(REPLAY_PATHS[schedule_id])
        all_replay_rows.extend(replay)
        replay_contract &= (
            len(replay) == 4576
            and [row["event_id"] for row in replay] == [row["event_id"] for row in current]
            and Counter(row["decision"] for row in replay) == expected_decisions[schedule_id]
            and sum(row["recipe_replaced"] == "YES" for row in replay) == 1026
        )
        for index, row in enumerate(replay):
            expected_recipe = schedule_by_event[schedule_id].get(row["event_id"], row["source_recipe"])
            replay_contract &= row["visible_recipe"] == expected_recipe
            expected_next = "NONE"
            if index + 1 < len(replay):
                nxt = replay[index + 1]
                if nxt["statement_id"] == row["statement_id"] and nxt["physical_page"] == row["physical_page"] and nxt["owner_de"] == row["owner_de"]:
                    expected_next = nxt["visible_recipe"]
            lookahead_contract &= row["visible_next_recipe"] == expected_next
            if row["decision"] == "STOP":
                stop_safety &= (
                    row["stop_preserves_state"] == "YES"
                    and row["incoming_action"] == row["outgoing_action"]
                    and row["incoming_argument"] == row["outgoing_argument"]
                    and row["scope_incoming_action"] == row["scope_outgoing_action"]
                )
                if row["recipe_replaced"] == "NO":
                    untouched_stop_counter[(schedule_id, row["event_id"])] += 1
    check("replay_contract", replay_contract, "six complete 4576-event replays")
    check("lookahead_contract", lookahead_contract, "one card, same statement/page/owner")
    check("all_stop_state_safe", stop_safety, "213/213")
    check("total_replay_count", len(all_replay_rows) == 27456, f"observed={len(all_replay_rows)}")
    check("only_two_unmutated_stops", untouched_stop_counter == Counter({
        ("LEX_FIRST", "G407-E1391"): 1,
        ("DELETION_FIRST", "G407-E1391"): 1,
    }), str(untouched_stop_counter))
    check("unmutated_stop_recovery", len(unmutated_stops) == 2 and all(
        row["event_id"] == "G407-E1391"
        and row["source_recipe"] == "EEE+DY"
        and row["blocked_factor_rules"] == "CLOSE:NO_ACTIVE_ACTION"
        and row["stop_preserves_state"] == "YES"
        and row["recovery_event_id"] == "G407-E1392"
        and row["recovery_decision"] == "READ"
        and row["same_bank_card_distance"] == "1"
        for row in unmutated_stops
    ), "known f72r dependent close, one-card recovery")

    check("owner_bank_isolation", all(
        row["isolated_global_all_exact"] == "YES"
        and row["isolated_global_exact_count"] == row["event_count"]
        for row in banks
    ), "342/342 banks")
    check("owner_bank_event_count", sum(int(row["event_count"]) for row in banks) == 27456, "six times 4576")
    check("burst_recovery_totals", Counter(row["recovery_before_next_fault"] for row in recoveries) == Counter({
        "STATE_PARITY_BEFORE_NEXT_FAULT": 2554,
        "NEXT_FAULT_BEFORE_PARITY": 460,
        "BANK_END_RESET_ISOLATES_DIVERGENCE": 64,
    }), str(Counter(row["recovery_before_next_fault"] for row in recoveries)))
    check("burst_position_stop_safe", all(
        (row["first_decision"] != "STOP" or row["first_stop_safe"] == "YES")
        and (row["second_decision"] != "STOP" or row["second_stop_safe"] == "YES")
        for row in recoveries
    ), "all 3078 bursts")
    check("summary_no_selection_outcome", all(
        row["identity_override_count"] == "0"
        and row["advisory_override_count"] == "0"
        and row["stop_state_failure_count"] == "0"
        and row["owner_bank_exact_count"] == "57"
        and row["owner_bank_event_exact_count"] == "4576"
        for row in summaries
    ), "six summaries")
    check("no_sealed_pages", all(not row["physical_page"].lower().startswith("f84") for row in all_replay_rows), "fixed current pages only")
    check("result_counts", (
        result["schedule_count"] == 6
        and result["total_replay_event_count"] == 27456
        and result["total_burst_count"] == 3078
        and result["total_replacement_count"] == 6156
        and result["total_stop_count"] == 213
        and result["total_unmutated_stop_count"] == 2
        and result["owner_bank_isolation_exact_count"] == 342
    ), "compact result matches all ledgers")
    check("claim_ceiling_zeros", all(result[key] == 0 for key in (
        "outcome_fields_used_for_selection", "identity_overrides", "advisory_overrides",
        "meaning_revisions", "surface_predictions", "occurrence_predictions", "new_pages",
    )), "no forbidden promotions")

    before = {path: sha256(path) for path in DETERMINISTIC_OUTPUTS}
    run.main()
    after = {path: sha256(path) for path in DETERMINISTIC_OUTPUTS}
    check("deterministic_rebuild", before == after, "all 13 generated artifacts byte-identical")
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
