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
    events = read("FOUR_HUNDRED_THIRTY_SEVENTH_REVISED_B2_62_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_SEVENTH_REVISED_B2_22_STATEMENTS.tsv")
    ladder = read("FOUR_HUNDRED_THIRTY_SEVENTH_B2_GRADE_LADDER.tsv")
    dictionary = read("FOUR_HUNDRED_THIRTY_SEVENTH_B2_46_CARD_DICTIONARY.tsv")
    checks = {
        "events_62": len(events) == 62,
        "statements_22": len(statements) == 22,
        "ladder_cards_8": len(ladder) == 8,
        "ladder_events_15": sum(int(row["events"]) for row in ladder) == 15,
        "short_long_full_present": {row["grade"] for row in ladder} == {"KURZ", "LAENGER", "VOLL"},
        "open_close_present": {row["endpoint"] for row in ladder} == {"OPEN", "CLOSE"},
        "new_grade_cards_6": sum(row["source"] == "B2_NEW" for row in ladder) == 6,
        "B2_productive_14": sum(row["drawer"] == "B2_PRODUCTIVE_COMPOSITION" for row in dictionary) == 14,
        "B2_local_18": sum(row["drawer"] == "B2_LOCAL_WHOLE_CARD" for row in dictionary) == 18,
        "oteey_is_action": all(row["small_value_de"] == "nächsten Posten länger halten" for row in events if row["surface"] == "oteey"),
        "all_values": all(row["small_value_de"] for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
