#!/usr/bin/env python3
"""Validate Pass 729 quantity split."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SEVEN_HUNDRED_TWENTY_NINTH_3_QUANTITY_ROOTS.tsv")
    qcards = read("SEVEN_HUNDRED_TWENTY_NINTH_21_QUANTITY_CARDS.tsv")
    occurrences = read("SEVEN_HUNDRED_TWENTY_NINTH_61_QUANTITY_OCCURRENCES.tsv")
    cards = read("SEVEN_HUNDRED_TWENTY_NINTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_TWENTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_TWENTY_NINTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_TWENTY_NINTH_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_TWENTY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_root = {row["root"]: row for row in roots}
    checks = {
        "root_values_exact": {root: row["short_value_de"] for root, row in by_root.items()} == {"AIIN": "SOLLMASS", "AIN": "PORTION", "IIN": "ARBEITSSTUFE"},
        "root_counts_exact": {root: (int(row["exact_cards"]), int(row["events"])) for root, row in by_root.items()} == {"AIIN": (10, 39), "AIN": (8, 18), "IIN": (3, 4)},
        "quantity_cards_21_unique": len(qcards) == 21 and len({row["exact_card_id"] for row in qcards}) == 21,
        "occurrences_61_unique": len(occurrences) == 61 and len({row["event_id"] for row in occurrences}) == 61,
        "complete_173_381_116_11": len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(records) == 11,
        "unique_ids": len({row["exact_card_id"] for row in cards}) == 173 and len({row["event_id"] for row in events}) == 381 and len({row["statement_id"] for row in statements}) == 116,
        "event_card_readings_match": all(next(card["pass729_reading_de"] for card in cards if card["exact_card_id"] == row["card_no"]) == row["pass729_semantic_de"] for row in events),
        "all_aiin_sollmass": all("SOLLMASS" in row["pass729_atomic_reading_de"] for row in occurrences if row["root"] == "AIIN"),
        "all_ain_portion": all("PORTION" in row["pass729_atomic_reading_de"] for row in occurrences if row["root"] == "AIN"),
        "all_iin_workstage": all("ARBEITSSTUFE" in row["pass729_atomic_reading_de"] for row in occurrences if row["root"] == "IIN"),
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
