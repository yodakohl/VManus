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
    trace = read("FIVE_HUNDRED_NINETY_EIGHTH_116_STATE_TRACE.tsv")
    resets = read("FIVE_HUNDRED_NINETY_EIGHTH_10_OWNER_RESETS.tsv")
    records = read("FIVE_HUNDRED_NINETY_EIGHTH_11_RECORD_PROCESS_CHAINS.tsv")
    boundaries = read("FIVE_HUNDRED_NINETY_EIGHTH_10_INTER_RECORD_BOUNDARIES.tsv")
    machine = read("FIVE_HUNDRED_NINETY_EIGHTH_FIVE_TRANSITION_RULES.tsv")
    counts = Counter(row["transition"] for row in trace)
    checks = {
        "trace116": len(trace) == 116 and len({row["statement_id"] for row in trace}) == 116,
        "transition_counts": counts == Counter({"EXPLICIT_LOCAL_CONTINUATION": 41, "SAME_OWNER_UNSPECIFIED_STEP": 29, "CURRENT_ITEM_CONTINUATION": 25, "RECORD_INITIALIZE": 11, "OWNER_RESET": 10}),
        "resets10": len(resets) == 10 and all(row["cross_owner_carry"] == "FORBIDDEN_WITHOUT_MASTER_HANDOFF" for row in resets),
        "records11": len(records) == 11 and sum(int(row["statements"]) for row in records) == 116 and sum(int(row["events"]) for row in records) == 381,
        "owner_states21": sum(int(row["owner_states"]) for row in records) == 21,
        "boundaries10": len(boundaries) == 10,
        "one_possible_resume": sum(row["boundary_reading"] == "SAME_PLANT_RESUMPTION_POSSIBLE" for row in boundaries) == 1,
        "nine_hard_resets": sum(row["boundary_reading"] == "HARD_RECORD_RESET" for row in boundaries) == 9,
        "machine5": len(machine) == 5 and sum(int(row["count"]) for row in machine) == 116,
        "no_global_join": all(row["global_pipe_or_process_join"] == "NONE" for row in trace) and all(row["global_process_claim"] == "NONE__RECORD_LOCAL_ONLY" for row in records),
        "all_instructions": all(row["complete_instruction_de"] for row in trace),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
