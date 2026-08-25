#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BIO = {"f75r", "f81v", "f82r", "f83r"}


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    codebook = read("PASS989_159_CODEBOOK.tsv")
    events = read("PASS989_2511_EVENT_INTERLINEAR.tsv")
    roots = read("PASS989_53_ROOT_DICTIONARY.tsv")
    clauses = read("PASS989_354_COMPLETE_CLAUSE_EDITION.tsv")
    addresses = read("PASS989_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = read("PASS989_14_PAGE_READABLE_EDITION.tsv")
    labels = read("PASS989_16_F88R_INGREDIENT_LABELS.tsv")
    batches = read("PASS989_THREE_F88R_BATCHES.tsv")
    root_by_id = {row["root_id"]: row["atomic_meaning_de"] for row in roots}
    codebook_by_id = {row["teaching_unit_id"]: row for row in codebook}
    clause_event_ids = [event_id for row in clauses for event_id in row["event_ids"].split("|")]
    address_ids = [row["event_id"] for row in addresses]
    label_event_ids = {row["event_id"] for row in labels}
    f88_addresses = [row for row in addresses if row["event_id"] in label_event_ids]
    checks = {
        "codebook_159": len(codebook) == 159 and len(codebook_by_id) == 159,
        "roots_53": len(roots) == 53,
        "root_values_reconciled": all(codebook_by_id[root_id]["spoken_value_de"] == value for root_id, value in root_by_id.items()),
        "events_2511": len(events) == 2511 and len({row["event_id"] for row in events}) == 2511,
        "clauses_354": len(clauses) == 354,
        "clause_events_2010": len(clause_event_ids) == len(set(clause_event_ids)) == 2010,
        "addresses_501": len(address_ids) == len(set(address_ids)) == 501,
        "complete_event_partition": set(clause_event_ids) | set(address_ids) == {row["event_id"] for row in events}
        and not set(clause_event_ids) & set(address_ids),
        "pages_14": len(pages) == 14 and sum(int(row["events"]) for row in pages) == 2511,
        "bio_clauses_318_natural": sum(row["physical_page"] in BIO for row in clauses) == 318
        and all(row["reading_source"] in {"MANUAL_LONG_CLAUSE_REWRITE", "COMPACT_OWNER_ACTION_REWRITE"} for row in clauses if row["physical_page"] in BIO),
        "bio_events_1280": sum(int(row["event_count"]) for row in clauses if row["physical_page"] in BIO) == 1280,
        "f88_labels_16": len(labels) == 16 and len(label_event_ids) == 16,
        "f88_batch_shape_6_6_4": [int(row["label_count"]) for row in batches] == [6, 6, 4],
        "f88_all_ingredient_labels": all(row["visual_role"] == "INGREDIENT_LABEL" for row in labels),
        "f88_address_rows_16": len(f88_addresses) == 16,
        "f88_no_text_headings": all("THREE_SILENT_VESSEL_BATCHES_6_6_4" == row["diagram_model"] for row in f88_addresses),
        "f88_short_defaults_concrete": all(codebook_by_id[row["teaching_unit_id"]]["spoken_value_de"] not in {"TOP_01", "MID_01", "BOT_01"} for row in labels),
        "no_old_root_tokens_in_events": all("DIES" not in row["complete_working_reading_de"].split(" · ") and "SCHLIESSEN" not in row["complete_working_reading_de"].split(" · ") for row in events),
        "all_readings_present": all(row["complete_working_reading_de"] for row in events)
        and all(row["complete_working_translation_de"] for row in clauses)
        and all(row["complete_working_translation_de"] for row in pages),
        "sealed_absent": all("f84" not in row["physical_page"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS989_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
