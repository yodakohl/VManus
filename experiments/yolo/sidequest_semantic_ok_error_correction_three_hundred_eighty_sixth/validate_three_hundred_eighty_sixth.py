#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    repairs = read("THREE_HUNDRED_EIGHTY_SIXTH_THREE_ERROR_REPAIRS.tsv")
    trace = read("THREE_HUNDRED_EIGHTY_SIXTH_ELEVEN_POSITION_TRACE.tsv")
    checks = {
        "three_repairs": len(repairs) == 3,
        "eleven_positions": len(trace) == 11,
        "one_change_each": all(row["cards_changed"] == "1" for row in repairs),
        "other_cards_preserved": all(row["all_other_cards_preserved"] == "YES" for row in repairs),
        "existing_cards_only": all(row["surface_inventory_status"] == "BOTH_EXISTING_REGISTERED_CARDS" for row in repairs),
        "fault_types": Counter(row["faulty_component"] for row in repairs) == {"ENDPOINT": 1, "GRADE": 2},
        "one_changed_trace_each": Counter(row["exercise"] for row in trace if row["changed"] == "YES") == {"E1": 1, "E2": 1, "E3": 1},
        "repair_exact": all(row["repair_result"] == "EXACT_INTENDED_TRACK" for row in repairs),
        "components_preserved": all(row["repair_preserves_other_components"] == "YES" for row in trace),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_SIXTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
