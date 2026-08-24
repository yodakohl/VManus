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
    trace = read("FOUR_HUNDRED_NINETY_FIRST_10_EVENT_EXTRACTION_TRACE.tsv")
    objects = read("FOUR_HUNDRED_NINETY_FIRST_EIGHT_EXTRACTION_OBJECTS.tsv")
    edges = read("FOUR_HUNDRED_NINETY_FIRST_10_EXTRACTION_EDGES.tsv")
    candidates = read("FOUR_HUNDRED_NINETY_FIRST_THREE_HERBAL_MACRO_READINGS.tsv")
    comparison = read("FOUR_HUNDRED_NINETY_FIRST_H1_B1_TWO_PASS_COMPARISON.tsv")
    manual = read("FOUR_HUNDRED_NINETY_FIRST_169_ITEM_THREE_MACRO_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_NINETY_FIRST_776_THREE_MACRO_LEDGER.tsv")
    checks = {
        "trace_10": len(trace) == 10,
        "event_ids_exact": [row["event_id"] for row in trace] == [f"E{index:03d}" for index in range(1, 11)],
        "three_phases": len({row["macro_phase"] for row in trace}) == 3,
        "objects_8": len(objects) == 8,
        "edges_10": len(edges) == 10,
        "one_selected": sum(row["decision"] == "SELECT" for row in candidates) == 1,
        "property_clause_rejected": sum(row["decision"] == "REJECT" for row in candidates) == 1,
        "comparison_5": len(comparison) == 5,
        "manual_169": len(manual) == 169,
        "ledger_776": len(ledger) == 776,
        "three_macro_events_40": sum(row["local_macro"] != "NONE" for row in ledger) == 40,
        "h1_macro_10": sum(row["local_macro"] == "PFLANZENAUSZUG ZWEIMAL ABZIEHEN UND DOSIEREN" for row in ledger) == 10,
        "fixed_page": {row["page"] for row in ledger if row["local_macro"] == "PFLANZENAUSZUG ZWEIMAL ABZIEHEN UND DOSIEREN"} == {"f10r"},
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_NINETY_FIRST_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
