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
    events = read("FOUR_HUNDRED_SEVENTY_SIXTH_381_EVENT_PHASES.tsv")
    segments = read("FOUR_HUNDRED_SEVENTY_SIXTH_PROSE_PHASE_SEGMENTS.tsv")
    records = read("FOUR_HUNDRED_SEVENTY_SIXTH_11_RECORD_PHASE_CHAINS.tsv")
    units = read("FOUR_HUNDRED_SEVENTY_SIXTH_14_PHASED_UNIT_EDITIONS.tsv")
    lexicon = read("FOUR_HUNDRED_SEVENTY_SIXTH_PHASE_LEXICON.tsv")
    segment_events = [event for row in segments for event in row["event_ids"].split("|")]
    checks = {
        "events_381": len(events) == 381,
        "event_ids_unique": len({row["event_id"] for row in events}) == 381,
        "nine_phases": {row["phase"] for row in lexicon} == {"SELECT", "PREPARE", "MEASURE", "MOVE", "APPLY", "HOLD", "CHECK", "COLLECT", "CLOSE"},
        "eight_action_phases_used": len({row["action_phase"] for row in events}) == 8,
        "segment_alignment_381": len(segment_events) == 381 and set(segment_events) == {row["event_id"] for row in events},
        "record_count_11": len(records) == 11,
        "record_events_381": sum(int(row["events"]) for row in records) == 381,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["events"]) for row in units) == 776,
        "all_close_events_end_segments": all(next(seg for seg in segments if row["event_id"] in seg["event_ids"].split("|"))["ends_with_close"] == "YES" for row in events if row["closes_step"] == "YES"),
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in events + records + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
