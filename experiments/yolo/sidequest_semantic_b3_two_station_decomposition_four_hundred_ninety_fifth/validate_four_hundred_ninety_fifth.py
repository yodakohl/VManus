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
    trace = read("FOUR_HUNDRED_NINETY_FIFTH_SEVEN_EVENT_TWO_STATION_TRACE.tsv")
    boundary = read("FOUR_HUNDRED_NINETY_FIFTH_SIX_BOUNDARY_DECISIONS.tsv")
    objects = read("FOUR_HUNDRED_NINETY_FIFTH_FIVE_LOCAL_OBJECTS.tsv")
    candidates = read("FOUR_HUNDRED_NINETY_FIFTH_THREE_TWO_STATION_READINGS.tsv")
    manual = read("FOUR_HUNDRED_NINETY_FIFTH_167_ITEM_TWO_STATION_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_NINETY_FIFTH_776_TWO_STATION_LEDGER.tsv")
    checks = {
        "trace_7": len(trace) == 7,
        "event_ids_exact": [r["event_id"] for r in trace] == [f"E{i:03d}" for i in range(285, 292)],
        "stations_2": {r["station"] for r in trace} == {"STATION_A", "STATION_B"},
        "boundary_rows_6": len(boundary) == 6,
        "one_owner_reset": sum(r["owner_action"].startswith("RESET") for r in boundary) == 1,
        "no_material_carry_at_reset": all(r["material_action"] == "DO_NOT_CARRY" for r in boundary if r["owner_action"].startswith("RESET")),
        "objects_5": len(objects) == 5,
        "no_object_crosses_gap": all(r["crosses_owner_gap"] == "NO" for r in objects),
        "one_selected": sum(r["decision"] == "SELECT" for r in candidates) == 1,
        "manual_167": len(manual) == 167,
        "b3_whole_removed": not any(r["item_id"] == "W:B3-S026" for r in manual),
        "ledger_776": len(ledger) == 776,
        "seven_macro_events_72": sum(r["local_macro"] != "NONE" for r in ledger) == 72,
        "b3_macro_7": sum(r["local_macro"].startswith("QUELLPOSTEN") for r in ledger) == 7,
        "one_close_at_station_b": [r["event_id"] for r in trace if r["closes_step"] == "YES"] == ["E291"],
        "sealed_pages_absent": not any("f84" in str(v).lower() for r in trace + ledger for v in r.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_NINETY_FIFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items(): print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()): raise SystemExit(1)


if __name__ == "__main__": main()
