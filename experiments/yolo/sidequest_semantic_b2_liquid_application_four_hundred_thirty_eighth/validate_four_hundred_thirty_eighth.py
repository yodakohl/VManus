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
    events = read("FOUR_HUNDRED_THIRTY_EIGHTH_REVISED_B2_62_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_EIGHTH_REVISED_B2_22_STATEMENTS.tsv")
    liquid = read("FOUR_HUNDRED_THIRTY_EIGHTH_NINE_LIQUID_APPLICATION_CARDS.tsv")
    revisions = read("FOUR_HUNDRED_THIRTY_EIGHTH_FOUR_REVISIONS.tsv")
    dictionary = read("FOUR_HUNDRED_THIRTY_EIGHTH_B2_46_CARD_DICTIONARY.tsv")
    checks = {
        "events_62": len(events) == 62,
        "statements_22": len(statements) == 22,
        "liquid_cards_9": len(liquid) == 9,
        "revisions_4": len(revisions) == 4,
        "dictionary_46": len(dictionary) == 46,
        "B1_transfer_14": sum(row["drawer"] == "B1_TRANSFER" for row in dictionary) == 14,
        "B2_productive_18": sum(row["drawer"] == "B2_PRODUCTIVE_COMPOSITION" for row in dictionary) == 18,
        "portable_whole_1": sum(row["drawer"] == "PORTABLE_RECURRENT_WHOLE_CARD" for row in dictionary) == 1,
        "B2_local_13": sum(row["drawer"] == "B2_LOCAL_WHOLE_CARD" for row in dictionary) == 13,
        "warmwater_removed": all(row["small_value_de"] != "Warmwasser" for row in events),
        "wet_site_removed": all(row["small_value_de"] != "benetzte Stelle" for row in events),
        "lower_outlet_removed": all(row["small_value_de"] != "unterer Ablauf" for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
