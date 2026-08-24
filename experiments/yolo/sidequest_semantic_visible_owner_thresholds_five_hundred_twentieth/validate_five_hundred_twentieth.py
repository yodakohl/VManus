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
    cues = read("FIVE_HUNDRED_TWENTIETH_TEN_VISIBLE_OWNER_THRESHOLDS.tsv")
    grammar = read("FIVE_HUNDRED_TWENTIETH_FOUR_OWNER_THRESHOLD_RULES.tsv")
    log = read("FIVE_HUNDRED_TWENTIETH_381_THRESHOLD_MASTER_LOG.tsv")
    decisions = read("FIVE_HUNDRED_TWENTIETH_FIFTY_CONSCIOUS_DECISIONS.tsv")
    checks = {
        "cues10": len(cues) == 10 and len({row["event_id"] for row in cues}) == 10,
        "status8_2": Counter(row["ownership_status"] for row in cues)
        == Counter({"DIRECT_VISIBLE": 8, "UNRESOLVED": 2}),
        "all_owner_choices_automatic": all(row["free_master_choice"] == "NO" for row in cues),
        "grammar4": len(grammar) == 4 and all(row["master_choice"] == "NO" for row in grammar),
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "free_owner_choice_zero": all(row["free_owner_choice"] == "NO" for row in log),
        "decisions50": len(decisions) == 50,
        "only_allograph_decisions": Counter(row["decision_type"] for row in decisions)
        == Counter({"ENTER_ALLOGRAPH_BLOCK": 50}),
        "conscious50": sum(row["threshold_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in log)
        == 50,
        "automatic331": sum(row["threshold_master_mode"] == "AUTOMATIC_FLOW" for row in log) == 331,
        "ten_threshold_events_marked": sum(row["visual_owner_threshold"] != "NONE" for row in log) == 10,
        "program_choice_stays_removed": all(row["program_selection_decision"] == "NONE" for row in log),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in cues + log + decisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTIETH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
