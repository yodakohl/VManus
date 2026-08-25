#!/usr/bin/env python3
"""Validate Pass 734 workshop inventory."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SEVEN_HUNDRED_THIRTY_FOURTH_6_INVENTORY_ROOTS.tsv")
    chain = read("SEVEN_HUNDRED_THIRTY_FOURTH_6_STAGE_DEFAULT_WORKFLOW.tsv")
    multi = read("SEVEN_HUNDRED_THIRTY_FOURTH_13_MULTI_INVENTORY_STATEMENTS.tsv")
    icards = read("SEVEN_HUNDRED_THIRTY_FOURTH_47_INVENTORY_CARDS.tsv")
    occurrences = read("SEVEN_HUNDRED_THIRTY_FOURTH_66_INVENTORY_OCCURRENCES.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_FOURTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_FOURTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_FOURTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_FOURTH_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_FOURTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["root"]: (row["short_value_de"], int(row["exact_cards"]), int(row["events"])) for row in roots}
    all_text = " ".join(row["pass734_reading_de"] for row in cards) + " " + " ".join(row["pass734_working_reading_de"] for row in statements)
    checks = {
        "root_counts_exact": values == {"HO": ("ZUTAT", 5, 8), "OR": ("ANSATZ", 10, 18), "O": ("ARBEITSGANG", 18, 19), "AIR": ("WASSER", 5, 5), "CKH": ("DURCHLASS", 9, 14), "SOLK": ("SAMMELSTELLE", 5, 7)},
        "chain_six": len(chain) == 6 and [int(row["stage"]) for row in chain] == [1, 2, 3, 4, 5, 6],
        "multi_statements_13": len(multi) == 13 and all(row["global_machine_claim"] == "NONE__LOCAL_TOOLKIT_ONLY" for row in multi),
        "inventory_cards_47": len(icards) == 47 and len({row["exact_card_id"] for row in icards}) == 47,
        "inventory_events_66": len(occurrences) == 66 and len({row["event_id"] for row in occurrences}) == 66,
        "complete_173_381_116_11": len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(records) == 11,
        "event_card_readings_match": all(next(card["pass734_reading_de"] for card in cards if card["exact_card_id"] == row["card_no"]) == row["pass734_reading_de"] for row in events),
        "solk_all_collection_site": all("SAMMELSTELLE" in row["pass734_reading_de"] for row in occurrences if "SOLK" in row["inventory_roots"].split("+")),
        "no_named_materials": not any(word in all_text.upper() for word in ["WEIN", "ÖL", "OEL", "HONIG"]),
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
