#!/usr/bin/env python3
"""Validate Pass 731 workflow memory roots."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SEVEN_HUNDRED_THIRTY_FIRST_3_WORKFLOW_ROOTS.tsv")
    overlaps = read("SEVEN_HUNDRED_THIRTY_FIRST_5_OVERLAP_CONSTRUCTIONS.tsv")
    wcards = read("SEVEN_HUNDRED_THIRTY_FIRST_46_WORKFLOW_CARDS.tsv")
    occurrences = read("SEVEN_HUNDRED_THIRTY_FIRST_85_WORKFLOW_OCCURRENCES.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_FIRST_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_FIRST_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_FIRST_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_FIRST_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["root"]: (row["short_value_de"], int(row["exact_cards"]), int(row["events"])) for row in roots}
    checks = {
        "roots_exact": values == {"OR": ("ANSATZ", 10, 18), "OL": ("WEITER", 25, 48), "OT": ("DANACH", 16, 26)},
        "overlaps_five": len(overlaps) == 5 and sum(int(row["events"]) for row in overlaps) == 7,
        "workflow_cards_46": len(wcards) == 46 and len({row["exact_card_id"] for row in wcards}) == 46,
        "occurrences_85": len(occurrences) == 85 and len({row["event_id"] for row in occurrences}) == 85,
        "complete_173_381_116_11": len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(records) == 11,
        "event_card_readings_match": all(next(card["pass731_reading_de"] for card in cards if card["exact_card_id"] == row["card_no"]) == row["pass731_semantic_de"] for row in events),
        "ol_all_continue": all("WEITER" in row["pass731_atomic_reading_de"] for row in occurrences if "OL" in row["roots"].split("+")),
        "or_all_preparation": all("ANSATZ" in row["pass731_atomic_reading_de"] for row in occurrences if "OR" in row["roots"].split("+")),
        "ot_all_then": all("DANACH" in row["pass731_atomic_reading_de"] for row in occurrences if "OT" in row["roots"].split("+")),
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
