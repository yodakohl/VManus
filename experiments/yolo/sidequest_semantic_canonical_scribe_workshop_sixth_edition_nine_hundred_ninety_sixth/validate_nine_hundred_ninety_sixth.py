#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    codebook = rows("PASS996_159_COMPLETE_CODEBOOK.tsv")
    roots = rows("PASS996_53_PORTABLE_ROOTS.tsv")
    specialists = rows("PASS996_56_SPECIALIST_HEADWORDS.tsv")
    events = rows("PASS996_2511_EVENT_INTERLINEAR.tsv")
    clauses = rows("PASS996_354_NATURAL_CLAUSE_EDITION.tsv")
    addresses = rows("PASS996_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = rows("PASS996_14_PAGE_READABLE_EDITION.tsv")
    bio_events = rows("PASS996_1280_BIOLOGICAL_EVENT_PHRASES.tsv")
    bio_clauses = rows("PASS996_318_BIOLOGICAL_CLAUSES.tsv")
    labels = rows("PASS996_16_F88R_INGREDIENT_LABELS.tsv")
    batches = rows("PASS996_THREE_F88R_BATCHES.tsv")
    drawer = rows("PASS996_70_SECOND_DRAWER_COMPOSITIONS.tsv")
    grid = rows("PASS996_EIGHT_BY_EIGHT_COMPOSITION_GRID.tsv")
    root_values = {row["root_id"]: row["atomic_meaning_de"] for row in roots}
    code_values = {row["teaching_unit_id"]: row["spoken_value_de"] for row in codebook}
    clause_event_total = sum(int(row["event_count"]) for row in clauses)
    payload = "\n".join(str(row) for row in codebook + roots + events + clauses + addresses)
    checks = {
        "codebook_159": len(codebook) == 159,
        "roots_53": len(roots) == 53,
        "specialists_56": len(specialists) == 56,
        "root_codebook_match": all(code_values.get(key) == value for key, value in root_values.items()),
        "events_2511": len(events) == 2511,
        "clauses_354": len(clauses) == 354,
        "clause_events_2010": clause_event_total == 2010,
        "addresses_501": len(addresses) == 501,
        "partition_2511": clause_event_total + len(addresses) == 2511,
        "pages_14": len(pages) == 14 and sum(int(row["events"]) for row in pages) == 2511,
        "bio_events_1280": len(bio_events) == 1280,
        "bio_clauses_318": len(bio_clauses) == 318,
        "labels_16": len(labels) == 16,
        "batches_6_6_4": sorted(int(row["label_count"]) for row in batches) == [4, 6, 6],
        "drawer_70_287": len(drawer) == 70 and sum(int(row["events"]) for row in drawer) == 287,
        "grid_64": len(grid) == 64,
        "short_values": {root_values[key] for key in ("R-AIIN", "R-AIN", "R-OR", "R-T", "R-R", "R-CARRIER_Q")}
        == {"MASS", "PORTION", "ANSATZ", "STELLEN", "MERKEN", "BEGINN"},
        "all_clauses_natural": all(" · " not in row["complete_working_translation_de"] for row in clauses),
        "all_values_present": all(row["complete_working_reading_de"].strip() for row in events),
        "sealed_absent": "f84" not in payload.lower(),
    }
    output_hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.glob("PASS996_*.tsv"))
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "output_hashes": output_hashes,
    }
    (HERE / "PASS996_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
