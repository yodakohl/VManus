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
    events = read("FOUR_HUNDRED_FIFTY_SEVENTH_381_EVENT_REVERSE_SELECTION.tsv")
    audit = read("FOUR_HUNDRED_FIFTY_SEVENTH_56_ALIAS_OCCURRENCE_AUDIT.tsv")
    rules = read("FOUR_HUNDRED_FIFTY_SEVENTH_NINE_ALIAS_RULES.tsv")
    cards = read("FOUR_HUNDRED_FIFTY_SEVENTH_173_CARD_DICTIONARY_WITH_SELECTION.tsv")
    checks = {
        "events_381": len(events) == 381,
        "event_order": [row["event_id"] for row in events] == [f"E{n:03d}" for n in range(1, 382)],
        "cards_173": len(cards) == 173,
        "rules_9": len(rules) == 9,
        "alias_events_56": len(audit) == 56,
        "selection_partition": [sum(row["selection_layer"] == layer for row in events) for layer in ("UNIQUE_VALUE", "LOCAL_CONTEXT", "STATEMENT_POSITION", "RECORD_RENDERER")] == [325, 24, 21, 11],
        "all_exact_recovered": all(row["exact_card_recovered"] == "YES" for row in events),
        "audit_recovered": all(row["recovered"] == "YES" for row in audit),
        "first_second_portion": [row["surface"] for row in audit if row["small_value_de"] == "eine Portion davon zuführen"] == ["ykain", "ykan"],
        "resumption_only_statement_start": all(row["statement_position"] == "1" for row in audit if row["expected_joint_tuple_id"] == "d665560c8ff80799a82c"),
        "shared_values_unchanged": all(row["small_value_de"] for row in events),
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
