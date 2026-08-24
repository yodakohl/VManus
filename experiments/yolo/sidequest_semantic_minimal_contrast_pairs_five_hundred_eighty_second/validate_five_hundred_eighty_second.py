#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    decisions = read("FIVE_HUNDRED_EIGHTY_SECOND_FIVE_MINIMAL_CONTRAST_DECISIONS.tsv")
    audit = read("FIVE_HUNDRED_EIGHTY_SECOND_PAIR_EVENT_AUDIT.tsv")
    dictionary = read("FIVE_HUNDRED_EIGHTY_SECOND_REVISED_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_EIGHTY_SECOND_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_SEQUENCES.tsv")
    spoken = {r["component"]: r["short_spoken_value_de"] for r in dictionary}
    checks = {
        "decisions5": len(decisions) == 5 and len({r["pair"] for r in decisions}) == 5,
        "merge1_keep4": sum(r["decision"] == "MERGE_SPOKEN_VALUE_KEEP_GRAPHIC_GRAMMAR" for r in decisions) == 1 and sum(r["decision"] == "KEEP_MINIMAL_CONTRAST" for r in decisions) == 4,
        "dictionary38": len(dictionary) == 38 and len({r["component"] for r in dictionary}) == 38,
        "spoken37": len(set(spoken.values())) == 37 and spoken["LS"] == spoken["OL"] == "fort",
        "contrasts": spoken["K"] != spoken["P"] and spoken["CH"] != spoken["CHD"] and spoken["AIIN"] != spoken["IIN"] and spoken["AL"] != spoken["OS"],
        "audit_nonempty": len(audit) > 0 and all(r["compact_statement_de"] for r in audit),
        "events381": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "event_complete": all(r["spoken_component_sequence_de"] for r in events),
        "fixed_pages": {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_EIGHTY_SECOND_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
