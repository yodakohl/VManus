#!/usr/bin/env python3
"""Validate the integrated entry-frame selection manual."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_eighth.py")], check=True)
    events = read("SIX_HUNDRED_NINETY_EIGHTH_381_ENTRY_FRAME_EVENTS.tsv")
    profiles = read("SIX_HUNDRED_NINETY_EIGHTH_RECORD_POSITION_PROFILES.tsv")
    priorities = read("SIX_HUNDRED_NINETY_EIGHTH_3_POSITION_PRIORITIES.tsv")
    rules = read("SIX_HUNDRED_NINETY_EIGHTH_4_CONTEXT_RULES.tsv")
    modes = read("SIX_HUNDRED_NINETY_EIGHTH_34_LOCAL_MODES.tsv")
    checks = {
        "three_eighty_one_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "single_multi_counts": Counter(row["multi_surface_card"] for row in events) == Counter({"YES": 202, "NO": 179}),
        "source_counts": Counter(row["renderer_source"] for row in events) == Counter({"GLOBAL_RULE_RENDERER": 314, "AUTOMATIC_CONTEXT_RULE": 8, "RESIDUAL_LOCUS_TABLE": 59}),
        "frame_counts": Counter(row["entry_frame"] for row in events) == Counter({"BARE": 177, "q": 82, "d": 36, "ch": 27, "s": 27, "che": 13, "t": 6, "sh": 6, "c": 6, "y": 1}),
        "position_counts": Counter(row["locus_position"] for row in events) == Counter({"MIDDLE": 267, "FIRST": 57, "LAST": 57}),
        "three_priorities": len(priorities) == 3,
        "four_context_rules": len(rules) == 4 and sum(int(row["events"]) for row in rules) == 8,
        "thirty_four_modes": len(modes) == 34 and sum(int(row["events"]) for row in modes) == 59,
        "profiles_cover_events": sum(int(row["events"]) for row in profiles) == 381,
        "no_semantic_frame_values": all("Wrapperwechsel" in row["reading_de"] for row in rules),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
