#!/usr/bin/env python3
"""Validate the complete CHK heat-grade pass."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("THREE_HUNDRED_TWENTY_FIRST_FIVE_CHK_EVENTS.tsv")
    statements = read("THREE_HUNDRED_TWENTY_FIRST_FIVE_REVISED_STATEMENTS.tsv")
    rule = read("THREE_HUNDRED_TWENTY_FIRST_CHK_GRADE_RULE.tsv")
    checks = {
        "five_events": len(events) == 5,
        "five_unique_events": len({x["event_id"] for x in events}) == 5,
        "two_exact_cards": len({x["joint_tuple_id"] for x in events}) == 2,
        "three_short_two_long": sum(x["atomic_value_de"] == "Kurzwärme" for x in events) == 3 and sum(x["atomic_value_de"] == "Langwärme" for x in events) == 2,
        "five_complete_statements": len(statements) == 5 and len({x["statement_id"] for x in statements}) == 5,
        "both_sections": {x["record_unit_id"][0] for x in events} == {"H", "B"},
        "four_components": {x["component"] for x in rule} == {"CHK", "E", "EE", "Y"},
        "nonterminal_referent": next(x for x in rule if x["component"] == "Y")["prediction"].endswith("nicht selbst."),
        "no_sealed_page": all("f84" not in "\t".join(x.values()).lower() for rows in [events, statements, rule] for x in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
