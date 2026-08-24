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
    events = read("FOUR_HUNDRED_TWENTY_EIGHTH_HERBAL_100_EVENT_ROLE_EDITION.tsv")
    operations = read("FOUR_HUNDRED_TWENTY_EIGHTH_NINETEEN_OPERATION_LEXICON.tsv")
    roles = read("FOUR_HUNDRED_TWENTY_EIGHTH_EIGHT_ROLE_CLASSES.tsv")
    templates = read("FOUR_HUNDRED_TWENTY_EIGHTH_FIVE_OPERATION_TEMPLATES.tsv")
    rules = read("FOUR_HUNDRED_TWENTY_EIGHTH_ELEVEN_PREDICTIVE_RULES.tsv")
    checks = {
        "one_hundred_events": len(events) == 100,
        "four_inherited_fixes": sum(row["pass428_inherited_fix"] != "NONE" for row in events) == 4,
        "every_role_assigned": all(row["role_class"] for row in events),
        "no_unknown_role": all("UNKNOWN" not in row["role_class"] for row in events),
        "nineteen_operations": len(operations) == 19,
        "operation_event_sum": sum(int(row["events"]) for row in operations) == sum(row["role_class"] == "OPERATION" for row in events),
        "eight_roles": len(roles) == 8,
        "role_event_sum": sum(int(row["events"]) for row in roles) == 100,
        "five_templates": len(templates) == 5,
        "eleven_rules": len(rules) == 11,
        "picture_nouns_not_operations": all(row["operation_core"] == "NONE" for row in events if row["role_class"] == "PICTURE_OR_MATERIAL_NOUN"),
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (events, operations, roles, templates, rules) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
