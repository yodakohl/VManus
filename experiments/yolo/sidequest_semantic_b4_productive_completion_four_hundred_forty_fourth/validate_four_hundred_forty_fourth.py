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
    events = read("FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_47_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_16_STATEMENTS.tsv")
    compositions = read("FOUR_HUNDRED_FORTY_FOURTH_THIRTEEN_NEW_COMPOSITIONS.tsv")
    local = read("FOUR_HUNDRED_FORTY_FOURTH_TWO_LOCAL_WHOLE_CARDS.tsv")
    dictionary = read("FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_34_CARD_DICTIONARY.tsv")
    checks = {
        "events_47": len(events) == 47,
        "statements_16": len(statements) == 16,
        "compositions_13": len(compositions) == 13,
        "local_2": len(local) == 2,
        "dictionary_34": len(dictionary) == 34,
        "transfer_19": sum(row["drawer"] == "B1_B2_B3_TRANSFER" for row in dictionary) == 19,
        "productive_13": sum(row["drawer"] == "B4_PRODUCTIVE_COMPOSITION" for row in dictionary) == 13,
        "local_2_again": sum(row["drawer"] == "B4_LOCAL_WHOLE_CARD" for row in dictionary) == 2,
        "events_32_13_2": [sum(int(row["events"]) for row in dictionary if row["drawer"] == drawer) for drawer in ("B1_B2_B3_TRANSFER", "B4_PRODUCTIVE_COMPOSITION", "B4_LOCAL_WHOLE_CARD")] == [32, 13, 2],
        "unsupported_labels_removed": all(value not in {row["small_value_de"] for row in events} for value in ("erste Öffnung", "zweite Waschung; Schluss", "Dauer", "Warmausguss", "über der Stelle")),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
