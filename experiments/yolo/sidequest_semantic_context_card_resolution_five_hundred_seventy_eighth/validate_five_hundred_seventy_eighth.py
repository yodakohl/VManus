#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = read("FIVE_HUNDRED_SEVENTY_EIGHTH_ELEVEN_INVARIANT_CARD_RULES.tsv")
    events = read("FIVE_HUNDRED_SEVENTY_EIGHTH_SEVENTY_OCCURRENCE_RESOLUTIONS.tsv")
    fills = read("FIVE_HUNDRED_SEVENTY_EIGHTH_OWNER_SLOT_FILL_RULES.tsv")
    checks = {
        "cards11": len(cards) == 11 and len({r["card_no"] for r in cards}) == 11,
        "events70": len(events) == 70 and len({r["event_id"] for r in events}) == 70,
        "fill_rules9": len(fills) == 9,
        "resolved": all(r["resolved"] == "YES" and r["invariant_operation_de"] for r in events),
        "no_new_wholes": all(r["new_whole_word_introduced"] == "NO" for r in cards + events),
        "component_values_stable": all(r["component_meaning_changed"] == "NO" for r in cards),
        "counts_match": {r["card_no"]: int(r["occurrences"]) for r in cards} == {card: sum(e["card_no"] == card for e in events) for card in {e["card_no"] for e in events}},
        "fixed_pages": {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SEVENTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
