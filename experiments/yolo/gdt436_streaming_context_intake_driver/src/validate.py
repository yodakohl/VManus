#!/usr/bin/env python3
"""Validate GDT436's oracle-free streaming context driver."""

from __future__ import annotations

import csv
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver"
OUT = BASE / "artifacts"
EVENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_4576_event_owner_local_edition.tsv"
REFERENCE = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
REGISTERS = {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt436_4576_oracle_free_stream_readings.tsv",
        OUT / "gdt436_715_oracle_free_statement_readings.tsv",
        OUT / "gdt436_owner_state_banks.tsv",
        OUT / "gdt436_245_future_card_state_readings.tsv",
        OUT / "gdt436_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    events = read_tsv(tracked[0])
    statements = read_tsv(tracked[1])
    banks = read_tsv(tracked[2])
    future = read_tsv(tracked[3])
    result = json.loads(tracked[4].read_text(encoding="utf-8"))
    source = read_tsv(EVENTS)
    reference = {row["global_running_event_id"]: row for row in read_tsv(REFERENCE)}
    source_header = set(source[0])

    with tempfile.TemporaryDirectory(prefix="gdt436_validate_") as temp_dir:
        cli_output = Path(temp_dir) / "stream.tsv"
        subprocess.run(
            ["python3", str(BASE / "src/stream_read.py"), "--input", str(EVENTS), "--output", str(cli_output)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cli_rows = read_tsv(cli_output)

    event_counts_by_bank = Counter((row["physical_page"], row["owner_de"]) for row in events)
    future_counts = Counter(row["component_recipe"] for row in future)
    readiness_by_card = {
        recipe: next(row["context_readiness"] for row in future if row["component_recipe"] == recipe)
        for recipe in future_counts
    }
    readiness_counts = Counter(readiness_by_card.values())
    source_ids = [row["global_running_event_id"] for row in source]
    output_ids = [row["event_id"] for row in events]
    base_fields = list(cli_rows[0])
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "source_has_no_inherited_oracle_fields": "inherited_action_root" not in source_header and "inherited_argument_root" not in source_header,
        "stream_rows_4576": len(events) == 4576 and len({row["event_id"] for row in events}) == 4576,
        "stream_order_matches_input": output_ids == source_ids,
        "all_current_recipes_t0": all(row["intake_tier"] == "T0_EXACT_OBSERVED" for row in events),
        "no_current_stops": all(row["reader_status"] == "READ_FROM_EXACT_RECIPE_AND_LEFT_CONTEXT" for row in events),
        "explicit_and_inherited_state_exact": all(row["state_matches_reference"] == "YES" for row in events),
        "all_event_clauses_exact": all(row["clause_matches_reference"] == "YES" and row["reader_clause_de"] == reference[row["event_id"]]["imperative_clause_de"] for row in events),
        "inherited_action_count_1598": sum(row["inherited_action_root"] != "NONE" for row in events) == 1598,
        "inherited_argument_count_2096": sum(row["inherited_argument_root"] != "NONE" for row in events) == 2096,
        "statements_715": len(statements) == 715 and len({row["global_statement_id"] for row in statements}) == 715,
        "all_statement_roundtrips_exact": all(row["statement_roundtrip_exact"] == "YES" for row in statements),
        "statement_event_total_4576": sum(int(row["event_count"]) for row in statements) == 4576,
        "owner_state_banks_57": len(banks) == len(event_counts_by_bank) == 57,
        "bank_ids_unique": len({row["state_bank_id"] for row in banks}) == 57,
        "bank_event_counts_exact": all(int(row["event_count"]) == event_counts_by_bank[(row["physical_page"], row["owner_de"])] for row in banks),
        "one_new_bank_marker_each": sum(row["state_bank_was_new"] == "YES" for row in events) == 57,
        "future_state_rows_245": len(future) == 245,
        "future_cards_49_five_registers_each": len(future_counts) == 49 and all(count == 5 for count in future_counts.values()),
        "future_registers_exact": {row["register"] for row in future} == REGISTERS,
        "future_readiness_counts_exact": readiness_counts == Counter({
            "SELF_CONTAINED_ACTION_AND_ARGUMENT": 21,
            "NEEDS_INCOMING_ACTION_FOR_FULL_CLAUSE": 14,
            "NEEDS_INCOMING_ARGUMENT_FOR_FULL_CLAUSE": 13,
            "NEEDS_INCOMING_ACTION_AND_ARGUMENT": 1,
        }),
        "self_contained_ignores_seed_state": all(row["empty_state_clause_de"] == row["state_supplied_clause_de"] for row in future if row["context_readiness"] == "SELF_CONTAINED_ACTION_AND_ARGUMENT"),
        "context_needing_cards_change_with_seed": all(row["empty_state_clause_de"] != row["state_supplied_clause_de"] for row in future if row["context_readiness"] != "SELF_CONTAINED_ACTION_AND_ARGUMENT"),
        "cli_rows_4576": len(cli_rows) == 4576,
        "cli_matches_builder_base_fields": all(all(cli_rows[i][field] == events[i][field] for field in base_fields) for i in range(4576)),
        "result_status_exact": result["status"] == "ORACLE_FREE_STREAMING_CONTEXT_DRIVER_COMPLETE",
        "result_event_counts_exact": result["streamed_event_count"] == result["event_state_roundtrip_exact_count"] == result["event_clause_roundtrip_exact_count"] == 4576,
        "result_statement_counts_exact": result["statement_count"] == result["statement_roundtrip_exact_count"] == 715,
        "result_bank_and_inheritance_counts_exact": result["owner_state_bank_count"] == 57 and result["inherited_action_event_count"] == 1598 and result["inherited_argument_event_count"] == 2096,
        "result_future_counts_exact": result["main_future_card_count"] == 49 and result["future_register_state_reading_count"] == 245 and result["future_card_readiness_counts"] == dict(sorted(readiness_counts.items())),
        "no_event_id_state_oracle": result["event_id_used_as_state_input"] == 0,
        "no_meaning_surface_page_change": result["new_meanings"] == result["surface_predictions"] == result["new_pages"] == 0,
        "no_forbidden_page_in_outputs": "f84" not in output_text.lower(),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt436_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
