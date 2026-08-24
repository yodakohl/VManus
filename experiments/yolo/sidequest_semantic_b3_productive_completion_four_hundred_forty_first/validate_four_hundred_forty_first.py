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
    events = read("FOUR_HUNDRED_FORTY_FIRST_REVISED_B3_86_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_FORTY_FIRST_REVISED_B3_34_STATEMENTS.tsv")
    table = read("FOUR_HUNDRED_FORTY_FIRST_SEVENTEEN_NEW_COMPOSITIONS.tsv")
    dictionary = read("FOUR_HUNDRED_FORTY_FIRST_B3_52_CARD_DICTIONARY.tsv")
    local = read("FOUR_HUNDRED_FORTY_FIRST_NINE_B3_LOCAL_WHOLE_CARDS.tsv")
    checks = {
        "events_86": len(events) == 86,
        "statements_34": len(statements) == 34,
        "new_compositions_17": len(table) == 17,
        "new_productive_events_23": sum(int(row["events"]) for row in table) == 23,
        "dictionary_52": len(dictionary) == 52,
        "transfers_26": sum(row["drawer"] == "B1_B2_TRANSFER" for row in dictionary) == 26,
        "productive_17": sum(row["drawer"] == "B3_PRODUCTIVE_COMPOSITION" for row in dictionary) == 17,
        "local_9": len(local) == 9,
        "local_events_9": sum(int(row["events"]) for row in local) == 9,
        "broad_vessel_removed": all(row["small_value_de"] != "breites Gefäß" for row in events),
        "lower_site_removed": all(row["small_value_de"] != "untere Stelle" for row in events),
        "lower_outlet_removed": all(row["small_value_de"] != "unterer Ablauf" for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
