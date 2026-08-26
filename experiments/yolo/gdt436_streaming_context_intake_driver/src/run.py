#!/usr/bin/env python3
"""Build the oracle-free streaming state driver and future-card readiness map."""

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
BASE = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver"
OUT = BASE / "artifacts"
EVENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_4576_event_owner_local_edition.tsv"
STATEMENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_715_statement_owner_local_edition.tsv"
REFERENCE_EVENTS = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
REFERENCE_STATEMENTS = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_715_imperative_statements.tsv"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
STREAM_READER = BASE / "src/stream_read.py"
COMPILER = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/src/run.py"
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(EVENTS)
    source_statements = read_tsv(STATEMENTS)
    reference_events = {row["global_running_event_id"]: row for row in read_tsv(REFERENCE_EVENTS)}
    reference_statements = {row["global_statement_id"]: row for row in read_tsv(REFERENCE_STATEMENTS)}
    stream = load_module("gdt436_stream_reader", STREAM_READER)
    compiler = load_module("gdt416_compiler", COMPILER)
    streamed = stream.stream_rows(source_events)

    audit_rows: list[dict[str, object]] = []
    for row in streamed:
        reference = reference_events[str(row["event_id"])]
        state_match = (
            row["explicit_action_roots"] == reference["explicit_action_roots"]
            and row["explicit_argument_roots"] == reference["explicit_argument_roots"]
            and row["inherited_action_root"] == reference["inherited_action_root"]
            and row["inherited_argument_root"] == reference["inherited_argument_root"]
        )
        clause_match = row["reader_clause_de"] == reference["imperative_clause_de"]
        audit_rows.append({
            **row,
            "reference_inherited_action_root": reference["inherited_action_root"],
            "reference_inherited_argument_root": reference["inherited_argument_root"],
            "state_matches_reference": "YES" if state_match else "NO",
            "clause_matches_reference": "YES" if clause_match else "NO",
        })
    write_tsv(OUT / "gdt436_4576_oracle_free_stream_readings.tsv", audit_rows, list(audit_rows[0]))

    stream_by_event = {str(row["event_id"]): row for row in streamed}
    statement_rows: list[dict[str, object]] = []
    for statement in source_statements:
        event_ids = statement["event_ids"].split("|")
        clauses = [str(stream_by_event[event_id]["reader_clause_de"]) for event_id in event_ids]
        predicted = " ".join(clauses)
        reference = reference_statements[statement["global_statement_id"]]
        statement_rows.append({
            "global_statement_id": statement["global_statement_id"],
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "owner_de": statement["owner_de"],
            "event_count": len(event_ids),
            "event_ids": statement["event_ids"],
            "oracle_free_imperative_reading_de": predicted,
            "reference_imperative_reading_de": reference["imperative_reading_de"],
            "statement_roundtrip_exact": "YES" if predicted == reference["imperative_reading_de"] else "NO",
        })
    write_tsv(OUT / "gdt436_715_oracle_free_statement_readings.tsv", statement_rows, list(statement_rows[0]))

    by_bank: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in streamed:
        by_bank[(str(row["physical_page"]), str(row["owner_de"]))].append(row)
    bank_rows: list[dict[str, object]] = []
    for index, ((page, owner), rows) in enumerate(sorted(by_bank.items()), start=1):
        bank_rows.append({
            "state_bank_id": f"BANK{index:03d}",
            "physical_page": page,
            "owner_de": owner,
            "register": rows[0]["register"],
            "event_count": len(rows),
            "first_event_id": rows[0]["event_id"],
            "last_event_id": rows[-1]["event_id"],
            "explicit_action_update_count": sum(row["explicit_action_roots"] != "NONE" for row in rows),
            "explicit_argument_update_count": sum(row["explicit_argument_roots"] != "NONE" for row in rows),
            "inherited_action_use_count": sum(row["inherited_action_root"] != "NONE" for row in rows),
            "inherited_argument_use_count": sum(row["inherited_argument_root"] != "NONE" for row in rows),
            "final_active_action": rows[-1]["active_action_after"],
            "final_active_argument": rows[-1]["active_argument_after"],
        })
    write_tsv(OUT / "gdt436_owner_state_banks.tsv", bank_rows, list(bank_rows[0]))

    main_cards = [
        row for row in read_tsv(CATALOG)
        if row["intake_tier"] in {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}
    ]
    readiness_rows: list[dict[str, object]] = []
    readiness_classes: Counter[str] = Counter()
    for card in sorted(main_cards, key=lambda row: row["component_recipe"]):
        atoms = card["component_recipe"].split("+")
        actions = [atom for atom in atoms if atom in compiler.ACTION_ROOTS]
        arguments = [atom for atom in atoms if atom in compiler.ARGUMENT_ROOTS]
        if actions and arguments:
            readiness = "SELF_CONTAINED_ACTION_AND_ARGUMENT"
        elif actions:
            readiness = "NEEDS_INCOMING_ARGUMENT_FOR_FULL_CLAUSE"
        elif arguments:
            readiness = "NEEDS_INCOMING_ACTION_FOR_FULL_CLAUSE"
        else:
            readiness = "NEEDS_INCOMING_ACTION_AND_ARGUMENT"
        readiness_classes[readiness] += 1
        inherited_action = "" if actions else "OK"
        inherited_argument = "" if arguments else "Y"
        for register in REGISTERS:
            readiness_rows.append({
                "component_recipe": card["component_recipe"],
                "intake_tier": card["intake_tier"],
                "register": register,
                "explicit_action_roots": "|".join(actions) or "NONE",
                "explicit_argument_roots": "|".join(arguments) or "NONE",
                "context_readiness": readiness,
                "required_incoming_action": "YES" if not actions else "NO",
                "required_incoming_argument": "YES" if not arguments else "NO",
                "empty_state_clause_de": compiler.render_clause(register, atoms, actions, "", ""),
                "sample_incoming_action": inherited_action or "NONE",
                "sample_incoming_argument": inherited_argument or "NONE",
                "state_supplied_clause_de": compiler.render_clause(register, atoms, actions, inherited_action, inherited_argument),
            })
    write_tsv(OUT / "gdt436_245_future_card_state_readings.tsv", readiness_rows, list(readiness_rows[0]))

    result = {
        "status": "ORACLE_FREE_STREAMING_CONTEXT_DRIVER_COMPLETE",
        "input_event_count": len(source_events),
        "streamed_event_count": len(streamed),
        "event_state_roundtrip_exact_count": sum(row["state_matches_reference"] == "YES" for row in audit_rows),
        "event_clause_roundtrip_exact_count": sum(row["clause_matches_reference"] == "YES" for row in audit_rows),
        "statement_count": len(statement_rows),
        "statement_roundtrip_exact_count": sum(row["statement_roundtrip_exact"] == "YES" for row in statement_rows),
        "owner_state_bank_count": len(bank_rows),
        "inherited_action_event_count": sum(row["inherited_action_root"] != "NONE" for row in streamed),
        "inherited_argument_event_count": sum(row["inherited_argument_root"] != "NONE" for row in streamed),
        "main_future_card_count": len(main_cards),
        "future_register_state_reading_count": len(readiness_rows),
        "future_card_readiness_counts": dict(sorted(readiness_classes.items())),
        "stopped_current_event_count": sum(str(row["reader_status"]).startswith("STOP") for row in streamed),
        "event_id_used_as_state_input": 0,
        "new_meanings": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt436_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
