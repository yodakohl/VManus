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
    trace = read("FOUR_HUNDRED_NINETY_SECOND_NINE_EVENT_DISPATCH_TRACE.tsv")
    y_rows = read("FOUR_HUNDRED_NINETY_SECOND_THREE_Y_ALLOGRAPHS_ONE_REFERENT.tsv")
    states = read("FOUR_HUNDRED_NINETY_SECOND_FIVE_DISPATCH_STATES.tsv")
    candidates = read("FOUR_HUNDRED_NINETY_SECOND_THREE_DISPATCH_READINGS.tsv")
    manual = read("FOUR_HUNDRED_NINETY_SECOND_169_ITEM_FOUR_MACRO_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_NINETY_SECOND_776_FOUR_MACRO_LEDGER.tsv")
    checks = {
        "trace_9": len(trace) == 9,
        "event_ids_exact": [row["event_id"] for row in trace] == [f"E{index:03d}" for index in range(15, 24)],
        "three_phases": len({row["macro_phase"] for row in trace}) == 3,
        "three_y_rows": len(y_rows) == 3,
        "y_surfaces_exact": [row["surface"] for row in y_rows] == ["dy", "chy", "shy"],
        "one_y_referent": len({row["referent_de"] for row in y_rows}) == 1,
        "states_5": len(states) == 5,
        "one_selected": sum(row["decision"] == "SELECT" for row in candidates) == 1,
        "manual_169": len(manual) == 169,
        "ledger_776": len(ledger) == 776,
        "four_macro_events_49": sum(row["local_macro"] != "NONE" for row in ledger) == 49,
        "h2_macro_9": sum(row["local_macro"] == "PFLANZENANSATZ AUF SOLLMASS EINSTELLEN UND WEITERGEBEN" for row in ledger) == 9,
        "fixed_page": {row["page"] for row in ledger if row["local_macro"] == "PFLANZENANSATZ AUF SOLLMASS EINSTELLEN UND WEITERGEBEN"} == {"f10r"},
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_NINETY_SECOND_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
