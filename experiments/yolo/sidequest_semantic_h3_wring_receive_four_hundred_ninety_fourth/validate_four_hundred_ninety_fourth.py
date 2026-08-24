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
    trace = read("FOUR_HUNDRED_NINETY_FOURTH_SEVEN_EVENT_WRING_RECEIVE_TRACE.tsv")
    coverage = read("FOUR_HUNDRED_NINETY_FOURTH_COMPLETE_EXISTING_ITEM_COVERAGE.tsv")
    stages = read("FOUR_HUNDRED_NINETY_FOURTH_FOUR_WRING_RECEIVE_STAGES.tsv")
    candidates = read("FOUR_HUNDRED_NINETY_FOURTH_THREE_H3_READINGS.tsv")
    manual = read("FOUR_HUNDRED_NINETY_FOURTH_168_ITEM_H3_DECOMPOSED_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_NINETY_FOURTH_776_H3_DECOMPOSED_LEDGER.tsv")
    checks = {
        "trace_7": len(trace) == 7,
        "event_ids_exact": [r["event_id"] for r in trace] == [f"E{i:03d}" for i in range(39, 46)],
        "three_phases": len({r["macro_phase"] for r in trace}) == 3,
        "coverage_7": len(coverage) == 7,
        "all_existing_items": all(r["already_in_pass493_manual"] == "YES" for r in coverage),
        "no_new_local_value": all(r["new_local_value_needed"] == "NO" for r in coverage),
        "stages_4": len(stages) == 4,
        "one_selected": sum(r["decision"] == "SELECT" for r in candidates) == 1,
        "manual_168": len(manual) == 168,
        "h3_whole_removed": not any(r["item_id"] == "W:H3-S001" for r in manual),
        "ledger_776": len(ledger) == 776,
        "six_macro_events_65": sum(r["local_macro"] != "NONE" for r in ledger) == 65,
        "h3_macro_7": sum(r["local_macro"].startswith("ANSATZ AUSWRINGEN") for r in ledger) == 7,
        "one_close_at_end": [r["event_id"] for r in trace if r["closes_step"] == "YES"] == ["E045"],
        "sealed_pages_absent": not any("f84" in str(v).lower() for r in trace + ledger for v in r.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_NINETY_FOURTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
