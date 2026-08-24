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
    flow = read("FOUR_HUNDRED_FIRST_24_EVENT_H2_FLOW.tsv")
    nodes = read("FOUR_HUNDRED_FIRST_11_OBJECT_NODES.tsv")
    comparison = read("FOUR_HUNDRED_FIRST_HERBAL_ORDER_COMPARISON.tsv")
    checks = {
        "twenty_four_events": len(flow) == 24,
        "complete_h2_range": [row["event_id"] for row in flow] == [f"E{number:03d}" for number in range(15, 39)],
        "three_statements": {row["statement_id"] for row in flow} == {"H2-S001", "H2-S002", "H2-S003"},
        "three_loci": {row["locus"] for row in flow} == {"f10r.6", "f10r.8", "f10r.9"},
        "eleven_nodes": len(nodes) == 11,
        "rejoin_present": any(row["operation"] == "REJOIN_PREVIOUS" for row in flow),
        "vessel_has_two_loads": sum(row["operation"] == "LOAD_BATCH" for row in flow) == 2,
        "external_application_final": flow[-1]["operation"] == "APPLY",
        "four_record_comparison": len(comparison) == 4,
        "all_cards_and_readings_present": all(row["joint_tuple_id"] and row["working_event_reading_de"] for row in flow),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_FIRST_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
