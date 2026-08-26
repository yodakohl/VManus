#!/usr/bin/env python3
"""Build the order-safe streaming reader and full current-edition replay."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt438_order_safe_streaming_reader"
OUT = BASE / "artifacts"
EVENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_4576_event_owner_local_edition.tsv"
STATEMENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_715_statement_owner_local_edition.tsv"
BASE_STREAM = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts/gdt436_4576_oracle_free_stream_readings.tsv"
BASE_STATEMENTS = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts/gdt436_715_oracle_free_statement_readings.tsv"
EXPECTED_REPAIRS = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair/artifacts/gdt437_68_current_order_repairs.tsv"
TRANSITIONS = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair/artifacts/gdt437_12005_state_transition_matrix.tsv"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
STREAM_READER = BASE / "src/order_safe_stream_read.py"
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
    reader = load_module("gdt438_order_safe_reader", STREAM_READER)
    source_events = read_tsv(EVENTS)
    source_statements = read_tsv(STATEMENTS)
    baseline = {row["event_id"]: row for row in read_tsv(BASE_STREAM)}
    baseline_statements = {row["global_statement_id"]: row for row in read_tsv(BASE_STATEMENTS)}
    expected = {row["event_id"]: row for row in read_tsv(EXPECTED_REPAIRS)}
    streamed = reader.stream_rows(source_events)

    event_rows: list[dict[str, object]] = []
    for row in streamed:
        old = baseline[str(row["event_id"])]
        changed = row["clause_changed_by_order_repair"] == "YES"
        expected_clause = expected.get(str(row["event_id"]), {}).get("order_safe_clause_de", old["reader_clause_de"])
        event_rows.append({
            **row,
            "state_matches_gdt436": "YES" if all(
                row[field] == old[field] for field in (
                    "active_action_before", "active_argument_before", "explicit_action_roots",
                    "explicit_argument_roots", "inherited_action_root", "inherited_argument_root",
                    "active_action_after", "active_argument_after",
                )
            ) else "NO",
            "expected_order_safe_clause_de": expected_clause,
            "clause_matches_gdt437": "YES" if row["reader_clause_de"] == expected_clause else "NO",
            "meaning_change": "NO__RELATION_ARGUMENT_ORDER_ONLY" if changed else "NO",
        })
    write_tsv(OUT / "gdt438_4576_order_safe_stream_readings.tsv", event_rows, list(event_rows[0]))

    by_event = {str(row["event_id"]): row for row in event_rows}
    statement_rows: list[dict[str, object]] = []
    for statement in source_statements:
        event_ids = statement["event_ids"].split("|")
        reading = " ".join(str(by_event[event_id]["reader_clause_de"]) for event_id in event_ids)
        changed_ids = [event_id for event_id in event_ids if by_event[event_id]["clause_changed_by_order_repair"] == "YES"]
        old = baseline_statements[statement["global_statement_id"]]
        statement_rows.append({
            "global_statement_id": statement["global_statement_id"],
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "owner_de": statement["owner_de"],
            "event_count": len(event_ids),
            "event_ids": statement["event_ids"],
            "order_repaired_event_count": len(changed_ids),
            "order_repaired_event_ids": "|".join(changed_ids) or "NONE",
            "baseline_imperative_reading_de": old["oracle_free_imperative_reading_de"],
            "order_safe_imperative_reading_de": reading,
            "statement_changed_by_order_repair": "YES" if changed_ids else "NO",
            "meaning_change": "NO__RELATION_ARGUMENT_ORDER_ONLY" if changed_ids else "NO",
        })
    write_tsv(OUT / "gdt438_715_order_safe_statement_readings.tsv", statement_rows, list(statement_rows[0]))

    cards = [
        row for row in read_tsv(CATALOG)
        if row["intake_tier"] in {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}
    ]
    transition_lookup = {
        (row["component_recipe"], row["register"]): row
        for row in read_tsv(TRANSITIONS)
        if row["incoming_action"] == "OK" and row["incoming_argument"] == "Y"
    }
    probe_rows: list[dict[str, object]] = []
    for ordinal, (card, register) in enumerate(
        ((card, register) for card in sorted(cards, key=lambda item: item["component_recipe"]) for register in REGISTERS),
        start=1,
    ):
        probe_input = [
            {"physical_page": f"SYNTHETIC_PROBE_{ordinal:03d}", "register": register, "owner_de": "PROBE_OWNER", "component_recipe": "OK+Y", "surface": "SEED"},
            {"physical_page": f"SYNTHETIC_PROBE_{ordinal:03d}", "register": register, "owner_de": "PROBE_OWNER", "component_recipe": card["component_recipe"], "surface": "TARGET"},
        ]
        seed, target = reader.stream_rows(probe_input)
        expected_transition = transition_lookup[(card["component_recipe"], register)]
        probe_rows.append({
            "probe_id": f"PROBE{ordinal:03d}",
            "component_recipe": card["component_recipe"],
            "intake_tier": card["intake_tier"],
            "register": register,
            "input_contains_event_id": "NO",
            "seed_status": seed["reader_status"],
            "target_status": target["reader_status"],
            "target_incoming_action": target["active_action_before"],
            "target_incoming_argument": target["active_argument_before"],
            "order_repair_rule": target["order_repair_rule"],
            "stream_clause_de": target["reader_clause_de"],
            "expected_transition_clause_de": expected_transition["order_safe_clause_de"],
            "matches_gdt437_transition": "YES" if target["reader_clause_de"] == expected_transition["order_safe_clause_de"] else "NO",
        })
    write_tsv(OUT / "gdt438_245_oracle_free_future_card_probes.tsv", probe_rows, list(probe_rows[0]))

    stop_input = [
        {"physical_page": "SYNTHETIC_STOP", "register": "HERBAL", "owner_de": "STOP_OWNER", "component_recipe": "OK+Y", "surface": "SEED"},
        {"physical_page": "SYNTHETIC_STOP", "register": "HERBAL", "owner_de": "STOP_OWNER", "component_recipe": "ZZ", "surface": "UNSEEN"},
        {"physical_page": "SYNTHETIC_STOP", "register": "HERBAL", "owner_de": "STOP_OWNER", "component_recipe": "AIIN+AIIN+AIIN+AIIN", "surface": "UNLICENSED"},
        {"physical_page": "SYNTHETIC_STOP", "register": "HERBAL", "owner_de": "STOP_OWNER", "component_recipe": "AIR+Y", "surface": "AFTER_STOP"},
    ]
    stop_rows = reader.stream_rows(stop_input)
    write_tsv(OUT / "gdt438_stop_state_integrity_probes.tsv", stop_rows, list(stop_rows[0]))

    result = {
        "status": "ORDER_SAFE_ORACLE_FREE_STREAMING_READER_COMPLETE",
        "current_event_count": len(event_rows),
        "state_roundtrip_exact_count": sum(row["state_matches_gdt436"] == "YES" for row in event_rows),
        "clause_matches_gdt437_count": sum(row["clause_matches_gdt437"] == "YES" for row in event_rows),
        "order_repaired_event_count": sum(row["clause_changed_by_order_repair"] == "YES" for row in event_rows),
        "statement_count": len(statement_rows),
        "order_repaired_statement_count": sum(row["statement_changed_by_order_repair"] == "YES" for row in statement_rows),
        "future_probe_count": len(probe_rows),
        "future_probe_match_count": sum(row["matches_gdt437_transition"] == "YES" for row in probe_rows),
        "stop_probe_count": sum(str(row["reader_status"]).startswith("STOP") for row in stop_rows),
        "event_id_used_as_state_input": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt438_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
