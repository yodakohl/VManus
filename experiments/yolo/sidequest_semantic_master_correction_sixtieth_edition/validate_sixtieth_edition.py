#!/usr/bin/env python3
"""Validate the master correction drills."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    exercises = rows("SIXTIETH_32_CORRECTION_EXERCISES.tsv")
    rules = rows("SIXTIETH_8_MASTER_CORRECTION_RULES.tsv")
    families = Counter(row["error_family"] for row in exercises)
    channels = Counter(row["detection_channel"] for row in exercises)
    checks = {
        "thirty_two_exercises": len(exercises) == 32 and len({row["exercise_id"] for row in exercises}) == 32,
        "eight_per_family": families == Counter({"GRADE_CHANGE": 8, "Y_CLOSE_CONFUSION": 8, "AL_AR_SWAP": 8, "DROP_DUPLICATE_REORDER": 8}),
        "eight_master_rules": len(rules) == 8 and Counter(row["error_family"] for row in rules) == Counter({name: 2 for name in families}),
        "detection_partition": channels == Counter({"LOCAL_CARD_READBACK": 16, "READBACK_PLUS_VISIBLE_OWNER": 8, "MASTER_EXEMPLAR_COMPARISON": 8}),
        "all_corruptions_change_atom_sequence": all(row["correct_atom_sequence"] != row["red_ink_corrupted_atom_sequence"] for row in exercises),
        "no_surface_invented": all(row["new_surface_invented"] == "NO_RED_INK_ATOM_DRILL_ONLY" for row in exercises),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in exercises),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "family_counts": dict(families), "channel_counts": dict(channels)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
