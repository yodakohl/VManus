#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    trace = read("FOUR_HUNDRED_NINETIETH_11_EVENT_TRANSFER_TRACE.tsv")
    states = read("FOUR_HUNDRED_NINETIETH_SIX_TRANSFER_STATES.tsv")
    edges = read("FOUR_HUNDRED_NINETIETH_11_TRANSFER_EDGES.tsv")
    comparison = read("FOUR_HUNDRED_NINETIETH_B1_B3_MACRO_COMPARISON.tsv")
    candidates = read("FOUR_HUNDRED_NINETIETH_THREE_TRANSFER_READINGS.tsv")
    manual = read("FOUR_HUNDRED_NINETIETH_169_ITEM_TWO_MACRO_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_NINETIETH_776_TWO_MACRO_LEDGER.tsv")
    checks = {
        "trace_11": len(trace) == 11,
        "event_ids_exact": [row["event_id"] for row in trace] == [f"E{index}" for index in range(270, 281)],
        "three_phases": len({row["macro_phase"] for row in trace}) == 3,
        "all_object_carried": all(row["state_transition"] == "ACTIVE_CARRIED" for row in trace),
        "states_6": len(states) == 6,
        "edges_11": len(edges) == 11,
        "comparison_7": len(comparison) == 7,
        "macros_distinct": all(row["same_macro"] != "YES" for row in comparison),
        "one_selected": sum(row["decision"] == "SELECT" for row in candidates) == 1,
        "manual_169": len(manual) == 169,
        "ledger_776": len(ledger) == 776,
        "two_macro_events_30": sum(row["local_macro"] != "NONE" for row in ledger) == 30,
        "b3_macro_11": sum(row["local_macro"] == "UEBERGABE MIT DOPPELTER SOLLPRUEFUNG" for row in ledger) == 11,
        "fixed_page": {row["page"] for row in ledger if row["local_macro"] == "UEBERGABE MIT DOPPELTER SOLLPRUEFUNG"} == {"f83r"},
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_NINETIETH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
