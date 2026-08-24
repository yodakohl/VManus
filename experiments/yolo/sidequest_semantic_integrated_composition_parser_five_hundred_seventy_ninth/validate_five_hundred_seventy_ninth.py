#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    manual = read("FIVE_HUNDRED_SEVENTY_NINTH_THIRTEEN_RULE_PARSER.tsv")
    events = read("FIVE_HUNDRED_SEVENTY_NINTH_THREE_HUNDRED_EIGHTY_ONE_PARSED_EVENTS.tsv")
    statements = read("FIVE_HUNDRED_SEVENTY_NINTH_ONE_HUNDRED_SIXTEEN_PARSED_STATEMENTS.tsv")
    inventory = read("FIVE_HUNDRED_SEVENTY_NINTH_PARSER_INVENTORY.tsv")
    checks = {
        "manual13": len(manual) == 13,
        "core94_fill9": {r["layer"]: int(r["items"]) for r in inventory}["COMPONENT_VALUES"] == 38 and {r["layer"]: int(r["items"]) for r in inventory}["ACTION_FRAMES"] == 56 and {r["layer"]: int(r["items"]) for r in inventory}["OWNER_SLOT_FILLS"] == 9,
        "events381": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "statements116": len(statements) == 116 and len({r["statement_id"] for r in statements}) == 116,
        "event_partition311_70": sum(r["context_selection"] == "PORTABLE_COMPONENT_READING" for r in events) == 311 and sum(r["context_selection"] == "OWNER_SLOT_FILL" for r in events) == 70,
        "no_whole_lookup": all(r["whole_card_gloss_lookup"] == "NO" for r in events),
        "event_complete": all(r["complete"] == "YES" and r["abstract_component_reading_de"] and r["contextual_card_reading_de"] for r in events),
        "statement_event_sum": sum(int(r["event_count"]) for r in statements) == 381 and all(r["all_events_complete"] == "YES" for r in statements),
        "fixed_pages": {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SEVENTY_NINTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
