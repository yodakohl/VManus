#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    owners = read("FIVE_HUNDRED_NINETEENTH_21_OWNER_TRANSITIONS.tsv")
    log = read("FIVE_HUNDRED_NINETEENTH_381_OWNER_AWARE_MASTER_LOG.tsv")
    decisions = read("FIVE_HUNDRED_NINETEENTH_60_CONSCIOUS_DECISIONS.tsv")
    records = read("FIVE_HUNDRED_NINETEENTH_ELEVEN_RECORD_OWNER_RULES.tsv")
    owner_types = Counter(row["transition_kind"] for row in owners)
    decision_types = Counter(row["decision_type"] for row in decisions)
    checks = {
        "owner_transitions21": len(owners) == 21 and len({row["event_id"] for row in owners}) == 21,
        "owner_split11_10": owner_types
        == Counter(
            {
                "AUTOMATIC_RECORD_OWNER_INITIALIZATION": 11,
                "CONSCIOUS_INTERNAL_VISIBLE_SCENE_SHIFT": 10,
            }
        ),
        "records11": len(records) == 11 and len({row["record"] for row in records}) == 11,
        "record_initializations_not_decisions": all(
            row["master_decision"] == "NO"
            for row in owners
            if row["transition_kind"] == "AUTOMATIC_RECORD_OWNER_INITIALIZATION"
        ),
        "internal_by_record4_4_2": Counter(
            row["record"] for row in owners if row["master_decision"] == "YES"
        )
        == Counter({"B2": 4, "B3": 4, "B4": 2}),
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "decisions60": len(decisions) == 60,
        "decision_types10_50": decision_types
        == Counter({"SHIFT_TO_VISIBLE_SUBSCENE": 10, "ENTER_ALLOGRAPH_BLOCK": 50}),
        "conscious57": sum(row["owner_revised_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in log)
        == 57,
        "automatic324": sum(row["owner_revised_master_mode"] == "AUTOMATIC_FLOW" for row in log) == 324,
        "allograph_blocks_preserved": sum(row["block_start_decision"] == "YES" for row in log) == 50,
        "program_choice_stays_removed": all(row["program_selection_decision"] == "NONE" for row in log),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in owners + log + decisions + records),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETEENTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
