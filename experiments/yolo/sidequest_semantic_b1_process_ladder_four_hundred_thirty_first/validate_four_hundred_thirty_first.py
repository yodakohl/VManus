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
    events = read("FOUR_HUNDRED_THIRTY_FIRST_REVISED_B1_66_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_FIRST_REVISED_B1_21_STATEMENTS.tsv")
    ladder = read("FOUR_HUNDRED_THIRTY_FIRST_B1_PROCESS_LADDER.tsv")
    phases = read("FOUR_HUNDRED_THIRTY_FIRST_FIVE_PROCESS_PHASES.tsv")
    ladder_ids = {row["joint_tuple_id"] for row in ladder}
    checks = {
        "B1_66": len(events) == 66,
        "statements_21": len(statements) == 21,
        "ladder_cards_9": len(ladder) == 9,
        "ladder_events_15": sum(int(row["events"]) for row in ladder) == 15,
        "ladder_event_count_matches": sum(row["joint_tuple_id"] in ladder_ids for row in events) == 15,
        "short_settle_four": [row for row in ladder if row["operation"] == "ABSETZEN"][0]["events"] == "4",
        "all_settle_short": all("kurz absetzen" in row["small_value_de"] for row in events if row["joint_tuple_id"] == "bc4f1f5c006c74a4d26d"),
        "five_phases": len(phases) == 5,
        "all_event_values": all(row["small_value_de"] for row in events),
        "all_statement_values": all(row["continuous_reading_de"] for row in statements),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
