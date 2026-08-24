#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    dictionary = read("FIVE_HUNDRED_EIGHTY_FIRST_THIRTY_EIGHT_SPOKEN_CORE_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_EIGHTY_FIRST_THREE_HUNDRED_EIGHTY_ONE_SPOKEN_EVENT_SEQUENCES.tsv")
    classes = read("FIVE_HUNDRED_EIGHTY_FIRST_SPOKEN_CLASS_SUMMARY.tsv")
    checks = {
        "dictionary38": len(dictionary) == 38 and len({r["component"] for r in dictionary}) == 38,
        "classes17_12_9": {r["workshop_class"]: int(r["components"]) for r in classes} == {"ACTION": 17, "ADDRESS_OR_CONTENT": 12, "GRAMMAR_SIGNAL": 9},
        "learning31_7": sum(r["learning_status"] == "RECURRENT_CORE" for r in dictionary) == 31 and sum(r["learning_status"] == "RARE_SPECIALIST" for r in dictionary) == 7,
        "nonempty_values": all(r["short_spoken_value_de"].strip() for r in dictionary),
        "owner_separate": all(r["visible_owner_spoken_here"] == "NO" for r in dictionary),
        "events381": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "event_complete": all(r["complete"] == "YES" and r["spoken_component_sequence_de"] and r["compact_statement_de"] for r in events),
        "owner_separate_events": all(r["owner_is_separate_from_spoken_dictionary"] == "YES" for r in events),
        "fixed_pages": {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_EIGHTY_FIRST_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
