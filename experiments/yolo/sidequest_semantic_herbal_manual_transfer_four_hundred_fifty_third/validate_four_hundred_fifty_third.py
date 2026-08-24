#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("FOUR_HUNDRED_FIFTY_THIRD_100_EVENT_HERBAL_EDITION.tsv")
    dictionary = read("FOUR_HUNDRED_FIFTY_THIRD_66_CARD_HERBAL_DICTIONARY.tsv")
    statements = read("FOUR_HUNDRED_FIFTY_THIRD_19_STATEMENT_HERBAL_EDITION.tsv")
    fields = read("FOUR_HUNDRED_FIFTY_THIRD_20_FIELD_HERBAL_EDITION.tsv")
    transfers = read("FOUR_HUNDRED_FIFTY_THIRD_17_TRANSFERRED_CARDS.tsv")
    pending = read("FOUR_HUNDRED_FIFTY_THIRD_49_PENDING_HERBAL_CARDS.tsv")
    revisions = read("FOUR_HUNDRED_FIFTY_THIRD_35_TRANSFER_REVISIONS.tsv")
    checks = {
        "records_5": {row["record_unit_id"] for row in events} == {f"H{n}" for n in range(1, 6)},
        "events_100": len(events) == 100,
        "events_e001_e100": [row["event_id"] for row in events] == [f"E{n:03d}" for n in range(1, 101)],
        "record_event_counts": [sum(row["record_unit_id"] == f"H{n}" for row in events) for n in range(1, 6)] == [14, 24, 17, 18, 27],
        "fields_20": len(fields) == 20,
        "statements_19": len(statements) == 19,
        "dictionary_66": len(dictionary) == 66,
        "transfers_17": len(transfers) == 17,
        "transferred_events_44": sum(row["lexicon_source"] == "BIOLOGICAL_EXACT_CARD_TRANSFER" for row in events) == 44,
        "pending_49": len(pending) == 49,
        "pending_events_56": sum(row["lexicon_source"] == "HERBAL_LOCAL_CARD_PENDING_REANALYSIS" for row in events) == 56,
        "revisions_35": len(revisions) == 35,
        "dictionary_event_agreement": all(next(card for card in dictionary if card["joint_tuple_id"] == row["joint_tuple_id"])["small_value_de"] == row["small_value_de"] for row in events),
        "statement_events_once": sorted((event_id for row in statements for event_id in row["event_ids"].split("|")), key=lambda event_id: int(event_id[1:])) == [f"E{n:03d}" for n in range(1, 101)],
        "owner_count_4": len({row["picture_owner"] for row in events}) == 4,
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"},
        "sealed_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
