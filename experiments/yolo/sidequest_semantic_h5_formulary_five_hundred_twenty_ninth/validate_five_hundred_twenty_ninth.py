#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = read("FIVE_HUNDRED_TWENTY_NINTH_H5_TWENTY_SEVEN_EVENT_REVERSE_BUILD.tsv")
    statements = read("FIVE_HUNDRED_TWENTY_NINTH_SIX_H5_STATEMENTS.tsv")
    stages = read("FIVE_HUNDRED_TWENTY_NINTH_NINE_STAGE_H5_RECIPE.tsv")
    formulary = read("FIVE_HUNDRED_TWENTY_NINTH_H3_H5_FORMULARY.tsv")
    staged_events = [event for row in stages for event in row["selected_event_ids"].split("|")]
    universal = {row["formulary_role"] for row in formulary if row["present_all_three"] == "YES"}
    measure = next(row for row in formulary if row["formulary_role"] == "EXACT_CARD_PROC009_AIIN")
    checks = {
        "events27": len(events) == 27 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(74, 101)],
        "statements6": len(statements) == 6,
        "stages9": len(stages) == 9,
        "stage_event_partition": len(staged_events) == 27 and set(staged_events) == {row["event_id"] for row in events},
        "every_card_has_source_clause": all(row["minimum_source_clause_de"] for row in events),
        "owner_consistent": {row["owner_source"] for row in events} == {"IMAGE_H5_WHOLE_MULTIHEAD_COILED_PLANT"},
        "surface_count27": sum(len(row["surfaces"].split()) for row in statements) == 27,
        "h5_s001_crosses_line": next(row for row in statements if row["statement_id"] == "H5-S001")["crosses_physical_line"] == "YES",
        "five_universal_primitives": {"ACTIVATE_CHARGE", "TARGET_HANDOFF", "METER_CHECK", "CONTINUE_USE", "CLOSE"} <= universal,
        "aiin_counts1_3_2": (measure["h3_count"], measure["h4_count"], measure["h5_count"]) == ("1", "3", "2"),
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
