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
    events = read("FOUR_HUNDRED_THIRTY_THIRD_REVISED_B1_66_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_THIRD_REVISED_B1_21_STATEMENTS.tsv")
    slots = read("FOUR_HUNDRED_THIRTY_THIRD_B1_S002_NINETEEN_SLOTS.tsv")
    candidates = read("FOUR_HUNDRED_THIRTY_THIRD_SHECKHAL_CANDIDATES.tsv")
    audit = read("FOUR_HUNDRED_THIRTY_THIRD_S002_EXACT_CARD_AUDIT.tsv")
    checks = {
        "B1_66": len(events) == 66,
        "statements_21": len(statements) == 21,
        "S002_slots_19": len(slots) == 19,
        "S002_event_range": [row["event_id"] for row in slots] == [f"E{i:03d}" for i in range(102, 121)],
        "S002_cards_16": len(audit) == 16,
        "sheckhal_selected": [row["candidate"] for row in candidates if row["decision"] == "SELECT"] == ["kurz an der Durchlassstelle"],
        "moderate_amount_withdrawn": [row["decision"] for row in candidates if row["candidate"] == "mäßige Menge"] == ["WITHDRAW"],
        "dl_is_short_additive": all(row["small_value_de"] == "Zusatz" for row in events if row["joint_tuple_id"] == "0f18de177ed7c878bf95"),
        "all_values": all(row["small_value_de"] for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
