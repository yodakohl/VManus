#!/usr/bin/env python3
"""Validate Pass 716 fresh docket copies."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    dockets = read("SEVEN_HUNDRED_SIXTEENTH_12_FRESH_DOCKETS.tsv")
    trace = read("SEVEN_HUNDRED_SIXTEENTH_27_FORWARD_BACKREAD_TRACE.tsv")
    checks = {
        "dockets_12": len(dockets) == 12,
        "events_27_unique": len(trace) == 27 and len({row["practice_event_id"] for row in trace}) == 27,
        "three_owner_classes": {row["owner_class"] for row in dockets} == {"PLANT", "BASIN", "APPARATUS"},
        "four_rules_exercised": {row["selection_rule"] for row in trace if row["selection_rule"].startswith("CR")} == {"CR1", "CR2", "CR3", "CR4"},
        "marked_and_plain": {row["selected_variant"] for row in trace if row["selected_variant"] != "UNIQUE"} == {"MARKED", "PLAIN"},
        "all_surfaces_unique": all(row["surface_unique_to_card"] == "YES" for row in trace),
        "no_old_event_ids": all(not row["practice_event_id"].startswith("E") for row in trace),
        "no_local_tray_lookups": all(row["local_surface_tray_lookup"] == "NONE" for row in trace),
        "all_sequences_nonempty": all(row["component_sequence"] and row["card_sequence"] and row["surface_sequence"] and row["backreading_de"] for row in dockets),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTEENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
