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
    events = read("FOUR_HUNDRED_FORTY_SIXTH_FINAL_20_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_FORTY_SIXTH_FINAL_FOUR_STATEMENTS.tsv")
    compositions = read("FOUR_HUNDRED_FORTY_SIXTH_SIX_NEW_COMPOSITIONS.tsv")
    wholes = read("FOUR_HUNDRED_FORTY_SIXTH_TWO_LOCAL_WHOLE_CARDS.tsv")
    dictionary = read("FOUR_HUNDRED_FORTY_SIXTH_FINAL_16_CARD_DICTIONARY.tsv")
    checks = {
        "events_20": len(events) == 20,
        "event_ids_complete": [row["event_id"] for row in events] == [f"E{n}" for n in range(362, 382)],
        "statements_4": len(statements) == 4,
        "cards_16": len(dictionary) == 16,
        "drawer_counts_8_6_2": [sum(row["drawer"] == drawer for row in dictionary) for drawer in ("B1_B2_B3_B4_TRANSFER", "B5_B6_PRODUCTIVE_COMPOSITION", "B5_B6_LOCAL_WHOLE_CARD")] == [8, 6, 2],
        "event_counts_12_6_2": [sum(int(row["events"]) for row in dictionary if row["drawer"] == drawer) for drawer in ("B1_B2_B3_B4_TRANSFER", "B5_B6_PRODUCTIVE_COMPOSITION", "B5_B6_LOCAL_WHOLE_CARD")] == [12, 6, 2],
        "compositions_6": len(compositions) == 6,
        "wholes_2": len(wholes) == 2,
        "openings_removed": all("Oeffnung" not in row["small_value_de"] for row in events),
        "raly_cools_current": next(row for row in events if row["event_id"] == "E375")["small_value_de"] == "dies abkuehlen",
        "record_restart_preserved": next(row for row in events if row["event_id"] == "E373")["record_restart_before"] == "YES",
        "no_empty_values": all(row["small_value_de"].strip() for row in events),
        "sealed_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
