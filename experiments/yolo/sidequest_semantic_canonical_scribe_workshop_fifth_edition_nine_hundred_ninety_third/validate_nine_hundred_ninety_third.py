#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BIO = {"f75r", "f81v", "f82r", "f83r"}


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    codebook = read("PASS993_159_COMPLETE_CODEBOOK.tsv")
    roots = read("PASS993_53_PORTABLE_ROOTS.tsv")
    specialists = read("PASS993_56_SPECIALIST_HEADWORDS.tsv")
    events = read("PASS993_2511_EVENT_INTERLINEAR.tsv")
    clauses = read("PASS993_354_NATURAL_CLAUSE_EDITION.tsv")
    addresses = read("PASS993_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = read("PASS993_14_PAGE_READABLE_EDITION.tsv")
    labels = read("PASS993_16_F88R_INGREDIENT_LABELS.tsv")
    batches = read("PASS993_THREE_F88R_BATCHES.tsv")
    bio_events = read("PASS993_1280_BIOLOGICAL_EVENT_PHRASES.tsv")
    bio_clauses = read("PASS993_318_BIOLOGICAL_CLAUSES.tsv")
    codebook_by_id = {row["teaching_unit_id"]: row for row in codebook}
    root_by_id = {row["root_id"]: row for row in roots}
    clause_event_ids = [event_id for row in clauses for event_id in row["event_ids"].split("|")]
    address_ids = [row["event_id"] for row in addresses]
    checks = {
        "codebook_159": len(codebook) == 159 and len(codebook_by_id) == 159,
        "roots_53": len(roots) == 53 and len(root_by_id) == 53,
        "specialists_56": len(specialists) == 56,
        "root_codebook_match": all(codebook_by_id[root_id]["spoken_value_de"] == row["atomic_meaning_de"] for root_id, row in root_by_id.items()),
        "events_2511": len(events) == 2511 and len({row["event_id"] for row in events}) == 2511,
        "clauses_354": len(clauses) == 354 and len({row["clause_id"] for row in clauses}) == 354,
        "clause_events_2010": len(clause_event_ids) == len(set(clause_event_ids)) == 2010,
        "addresses_501": len(address_ids) == len(set(address_ids)) == 501,
        "full_partition": set(clause_event_ids) | set(address_ids) == {row["event_id"] for row in events}
        and not set(clause_event_ids) & set(address_ids),
        "pages_14": len(pages) == 14 and sum(int(row["events"]) for row in pages) == 2511,
        "all_clauses_natural": all(row["complete_working_translation_de"] and " · " not in row["complete_working_translation_de"] for row in clauses),
        "bio_events_1280": len(bio_events) == 1280 and len({row["event_id"] for row in bio_events}) == 1280,
        "bio_clauses_318": len(bio_clauses) == 318 and sum(row["physical_page"] in BIO for row in clauses) == 318,
        "f88_labels_16": len(labels) == 16 and all(row["visual_role"] == "INGREDIENT_LABEL" for row in labels),
        "f88_batches_6_6_4": [int(row["label_count"]) for row in batches] == [6, 6, 4],
        "specialist_headwords_short": all(" " not in row["selected_headword_de"] for row in specialists),
        "sonderort_fixed": root_by_id["R-S_ADDR"]["atomic_meaning_de"] == "SONDERORT",
        "no_old_root_tokens": all("DIES" not in row["complete_working_reading_de"].split(" · ") and "SCHLIESSEN" not in row["complete_working_reading_de"].split(" · ") for row in events),
        "all_values_present": all(row["spoken_value_de"] and row["concrete_context_values_de"] for row in codebook)
        and all(row["complete_working_reading_de"] for row in events),
        "sealed_absent": all("f84" not in row["physical_page"].lower() for row in events),
    }
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.glob("PASS993_*.tsv"))
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "output_hashes": hashes}
    (HERE / "PASS993_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
