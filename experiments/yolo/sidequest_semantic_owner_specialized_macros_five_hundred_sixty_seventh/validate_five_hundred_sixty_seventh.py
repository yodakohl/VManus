#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    combos = read("FIVE_HUNDRED_SIXTY_SEVENTH_MACRO_OWNER_COMBINATIONS.tsv")
    statements = read("FIVE_HUNDRED_SIXTY_SEVENTH_ONE_HUNDRED_SIXTEEN_OWNER_SPECIALIZED_STATEMENTS.tsv")
    records = read("FIVE_HUNDRED_SIXTY_SEVENTH_ELEVEN_OWNER_SPECIALIZED_RECORDS.tsv")
    events = read("FIVE_HUNDRED_SIXTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv")
    checks = {
        "eight_owner_classes": len({row["owner_object_class"] for row in statements}) == 8,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "macro73_oneoff43": sum(row["macro_id"] != "NONE" for row in statements) == 73 and sum(row["macro_id"] == "NONE" for row in statements) == 43,
        "combo_sum73": sum(int(row["statements"]) for row in combos) == 73,
        "formal_macro_unchanged": all(row["formal_macro_unchanged"] == "YES" for row in combos),
        "records11": len(records) == 11 and sum(int(row["statements"]) for row in records) == 116,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "all_actions_visible": all(row["all_actions_visible"] == "YES" for row in statements),
        "events_retained": all(row["event_retained"] == "YES" for row in events),
        "no_generic_workstoff": all("Arbeitsstoff" not in row["owner_specialized_complete_reading_de"] for row in statements),
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
