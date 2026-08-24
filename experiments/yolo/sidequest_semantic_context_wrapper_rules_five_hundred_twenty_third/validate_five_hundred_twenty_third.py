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
    rules = read("FIVE_HUNDRED_TWENTY_THIRD_FOUR_CONTEXT_WRAPPER_RULES.tsv")
    residual = read("FIVE_HUNDRED_TWENTY_THIRD_FIFTY_NINE_RESIDUAL_ASSIGNMENTS.tsv")
    modes = read("FIVE_HUNDRED_TWENTY_THIRD_THIRTY_FOUR_RESIDUAL_LOCUS_TABLES.tsv")
    log = read("FIVE_HUNDRED_TWENTY_THIRD_381_CONTEXT_RENDERER_LOG.tsv")
    decisions = read("FIVE_HUNDRED_TWENTY_THIRD_THIRTY_FOUR_CONSCIOUS_DECISIONS.tsv")
    checks = {
        "rules4": len(rules) == 4 and all(row["support_events"] == "2" for row in rules),
        "zero_false_positives": all(row["false_positive_events"] == "0" for row in rules),
        "context_events8": sum(int(row["support_events"]) for row in rules) == 8,
        "residual59": len(residual) == 59 and len({row["event_id"] for row in residual}) == 59,
        "special_partition67": len(
            {event for row in rules for event in row["event_ids"].split("|")}
            | {row["event_id"] for row in residual}
        )
        == 67,
        "residual_modes34": len(modes) == 34 and len({row["residual_mode_id"] for row in modes}) == 34,
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "source_partition": Counter(row["wrapper_assignment_source"] for row in log)
        == Counter({"GLOBAL_RULE_RENDERER": 314, "AUTOMATIC_CONTEXT_RULE": 8, "RESIDUAL_LOCUS_TABLE": 59}),
        "decisions34": len(decisions) == 34,
        "only_residual_loads": Counter(row["decision_type"] for row in decisions)
        == Counter({"LOAD_RESIDUAL_LOCUS_TABLE": 34}),
        "conscious34": sum(row["context_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in log) == 34,
        "automatic347": sum(row["context_master_mode"] == "AUTOMATIC_FLOW" for row in log) == 347,
        "surface_roundtrip": all(row["stamp_output_surface"] == row["renderer_final_surface"] for row in log),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in residual + modes + log + decisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
