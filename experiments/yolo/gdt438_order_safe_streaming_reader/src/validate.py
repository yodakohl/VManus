#!/usr/bin/env python3
"""Validate GDT438's order-safe prospective streaming interface."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt438_order_safe_streaming_reader"
OUT = BASE / "artifacts"
EXPECTED = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair/artifacts/gdt437_68_current_order_repairs.tsv"
REGISTERS = {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt438_4576_order_safe_stream_readings.tsv",
        OUT / "gdt438_715_order_safe_statement_readings.tsv",
        OUT / "gdt438_245_oracle_free_future_card_probes.tsv",
        OUT / "gdt438_stop_state_integrity_probes.tsv",
        OUT / "gdt438_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    events = read_tsv(tracked[0])
    statements = read_tsv(tracked[1])
    probes = read_tsv(tracked[2])
    stops = read_tsv(tracked[3])
    result = json.loads(tracked[4].read_text(encoding="utf-8"))
    expected_ids = {row["event_id"] for row in read_tsv(EXPECTED)}
    changed = [row for row in events if row["clause_changed_by_order_repair"] == "YES"]
    changed_ids = {row["event_id"] for row in changed}
    statement_changed_ids = {
        event_id
        for row in statements if row["order_repaired_event_ids"] != "NONE"
        for event_id in row["order_repaired_event_ids"].split("|")
    }
    card_counts = Counter(row["component_recipe"] for row in probes)
    status_sequence = [row["reader_status"] for row in stops]
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "events_4576_unique": len(events) == 4576 and len({row["event_id"] for row in events}) == 4576,
        "events_all_read": all(row["reader_status"] == "READ_FROM_EXACT_RECIPE_AND_LEFT_CONTEXT" for row in events),
        "state_roundtrip_4576": all(row["state_matches_gdt436"] == "YES" for row in events),
        "clause_matches_gdt437_4576": all(row["clause_matches_gdt437"] == "YES" for row in events),
        "changed_events_68_exact": len(changed) == 68 and changed_ids == expected_ids,
        "changed_events_order_only": all(
            row["meaning_change"] == "NO__RELATION_ARGUMENT_ORDER_ONLY"
            and row["baseline_reader_clause_de"] != row["reader_clause_de"]
            and row["order_repair_rule"] in {"INHERITED_ACTION_RELATION_BEFORE_ARGUMENT", "REFERENCE_RELATION_BEFORE_ARGUMENT"}
            for row in changed
        ),
        "unchanged_events_really_unchanged": all(
            row["baseline_reader_clause_de"] == row["reader_clause_de"]
            for row in events if row["clause_changed_by_order_repair"] == "NO"
        ),
        "statements_715_unique": len(statements) == 715 and len({row["global_statement_id"] for row in statements}) == 715,
        "statement_event_total_4576": sum(int(row["event_count"]) for row in statements) == 4576,
        "changed_statements_59": sum(row["statement_changed_by_order_repair"] == "YES" for row in statements) == 59,
        "statement_changed_events_exact": statement_changed_ids == changed_ids and sum(int(row["order_repaired_event_count"]) for row in statements) == 68,
        "statement_wording_change_exact": all(
            (row["baseline_imperative_reading_de"] != row["order_safe_imperative_reading_de"])
            == (row["statement_changed_by_order_repair"] == "YES")
            for row in statements
        ),
        "future_probes_245": len(probes) == 245 and len(card_counts) == 49 and set(card_counts.values()) == {5},
        "future_probe_registers_exact": {row["register"] for row in probes} == REGISTERS,
        "future_probes_no_event_oracle": all(row["input_contains_event_id"] == "NO" for row in probes),
        "future_probe_seed_state_exact": all(row["target_incoming_action"] == "OK" and row["target_incoming_argument"] == "Y" for row in probes),
        "future_probe_matches_245": all(row["matches_gdt437_transition"] == "YES" for row in probes),
        "order_pair_separated_in_all_registers": all(
            next(row for row in probes if row["component_recipe"] == "AIR+Y" and row["register"] == register)["stream_clause_de"]
            != next(row for row in probes if row["component_recipe"] == "Y+AIR" and row["register"] == register)["stream_clause_de"]
            for register in REGISTERS
        ),
        "stop_probe_four_rows": len(stops) == 4,
        "stop_status_sequence_exact": status_sequence == [
            "READ_FROM_EXACT_RECIPE_AND_LEFT_CONTEXT", "STOP__UNSEEN_ATOM",
            "STOP__UNLICENSED_RECIPE", "READ_FROM_EXACT_RECIPE_AND_LEFT_CONTEXT",
        ],
        "stops_do_not_mutate_state": all(
            row["active_action_before"] == row["active_action_after"] == "OK"
            and row["active_argument_before"] == row["active_argument_after"] == "Y"
            for row in stops[1:3]
        ),
        "post_stop_state_restored": stops[3]["active_action_before"] == "OK" and stops[3]["active_argument_before"] == "Y",
        "result_status_exact": result["status"] == "ORDER_SAFE_ORACLE_FREE_STREAMING_READER_COMPLETE",
        "result_current_counts_exact": result["current_event_count"] == result["state_roundtrip_exact_count"] == result["clause_matches_gdt437_count"] == 4576 and result["order_repaired_event_count"] == 68,
        "result_statement_counts_exact": result["statement_count"] == 715 and result["order_repaired_statement_count"] == 59,
        "result_future_counts_exact": result["future_probe_count"] == result["future_probe_match_count"] == 245 and result["stop_probe_count"] == 2,
        "result_no_oracle_or_expansion": result["event_id_used_as_state_input"] == result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt438_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
