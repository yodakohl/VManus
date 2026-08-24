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
    trace = read("FOUR_HUNDRED_EIGHTY_NINTH_19_EVENT_MACRO_TRACE.tsv")
    nodes = read("FOUR_HUNDRED_EIGHTY_NINTH_NINE_OBJECT_NODES.tsv")
    edges = read("FOUR_HUNDRED_EIGHTY_NINTH_19_OBJECT_EDGES.tsv")
    candidates = read("FOUR_HUNDRED_EIGHTY_NINTH_THREE_MACRO_READINGS.tsv")
    manual = read("FOUR_HUNDRED_EIGHTY_NINTH_169_ITEM_MACRO_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_EIGHTY_NINTH_776_MACRO_REVISED_LEDGER.tsv")
    checks = {
        "trace_19": len(trace) == 19,
        "event_ids_exact": [row["event_id"] for row in trace] == [f"E{index}" for index in range(102, 121)],
        "three_phases": len({row["macro_phase"] for row in trace}) == 3,
        "nodes_9": len(nodes) == 9,
        "edges_19": len(edges) == 19,
        "edge_events_exact": [row["event_id"] for row in edges] == [row["event_id"] for row in trace],
        "three_candidates": len(candidates) == 3,
        "one_selected": sum(row["decision"] == "SELECT" for row in candidates) == 1,
        "manual_169": len(manual) == 169,
        "macro_manual_once": sum(row["item_id"] == "W:B1-S002" and "BECKENZULAUF" in row["teaching_value_or_rule_de"] for row in manual) == 1,
        "ledger_776": len(ledger) == 776,
        "macro_events_19": sum(row["local_macro"] != "NONE" for row in ledger) == 19,
        "surface_unchanged": all(row["observed_surface"] for row in ledger),
        "fixed_page": {row["page"] for row in ledger if row["local_macro"] != "NONE"} == {"f81v"},
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_NINTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
