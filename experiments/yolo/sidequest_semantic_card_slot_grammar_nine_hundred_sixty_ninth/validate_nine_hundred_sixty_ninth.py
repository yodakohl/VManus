#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read_tsv("PASS969_56_COMPONENT_SLOTS.tsv")
    events = read_tsv("PASS969_2511_SLOT_PARSES.tsv")
    patterns = read_tsv("PASS969_221_SLOT_PATTERNS.tsv")
    counts = Counter(row["collapsed_slot_pattern"] for row in events)
    checks = {
        "roots_56": len(roots) == 56 and len({row["component"] for row in roots}) == 56,
        "seven_slots": {row["primary_slot"] for row in roots} == {"FRAME", "ORDER", "ACTION", "GRADE", "ARGUMENT", "REFERENT", "CLOSE"},
        "events_2511": len(events) == 2511 and len({row["event_id"] for row in events}) == 2511,
        "patterns_221": len(patterns) == 221,
        "pattern_counts_exact": all(counts[row["slot_pattern"]] == int(row["events"]) for row in patterns),
        "top20_events_1938": sum(int(row["events"]) for row in patterns[:20]) == 1938,
        "action_argument_332": counts["ACTION>ARGUMENT"] == 332,
        "action_grade_referent_156": counts["ACTION>GRADE>REFERENT"] == 156,
        "action_grade_close_148": counts["ACTION>GRADE>CLOSE"] == 148,
        "all_components_slotted": not any("?" in row["component_slots"] for row in events),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in roots + events + patterns),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS969_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
