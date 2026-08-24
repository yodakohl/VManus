#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    profiles = read("FIVE_HUNDRED_SIXTY_EIGHTH_EIGHT_OWNER_MODIFIER_PROFILES.tsv")
    objects = read("FIVE_HUNDRED_SIXTY_EIGHTH_SIX_PORTABLE_WORKSHOP_OBJECTS.tsv")
    statements = read("FIVE_HUNDRED_SIXTY_EIGHTH_ONE_HUNDRED_SIXTEEN_OBJECT_STATEMENTS.tsv")
    events = read("FIVE_HUNDRED_SIXTY_EIGHTH_THREE_HUNDRED_EIGHTY_ONE_OBJECT_EVENTS.tsv")
    checks = {
        "profiles8": len(profiles) == 8 and len({row["owner_object_class"] for row in profiles}) == 8,
        "objects6": len(objects) == 6 and len({row["portable_object"] for row in objects}) == 6,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "profile_event_sum": sum(int(row["events"]) for row in profiles) == 381,
        "assignments_complete": all(row["object_assignment_complete"] == "YES" and row["portable_object_tags"].strip() for row in events),
        "statement_complete": all(row["object_inventory_complete"] == "YES" and row["portable_objects"].strip() for row in statements),
        "no_specific_substances": all("kein konkreter Stoffname" in row["not_asserted"] for row in objects),
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
