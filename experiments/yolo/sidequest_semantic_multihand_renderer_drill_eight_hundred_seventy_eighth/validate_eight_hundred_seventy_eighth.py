#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_EIGHTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_eighth.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    renderers = read(f"{PREFIX}_56_CORE_RENDERER_FAMILIES.tsv")
    events = read(f"{PREFIX}_261_CORE_RENDERER_EVENTS.tsv")
    drills = read(f"{PREFIX}_6_ORDER_ERROR_DRILLS.tsv")
    checks_table = read(f"{PREFIX}_5_CORRECTION_CHECKS.tsv")
    hands = read(f"{PREFIX}_4_HAND_PROFILES.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "renderer_56": len(renderers) == 56,
        "events_261": len(events) == 261 and len({row["order_mark_id"] for row in events}) == 261,
        "surfaces_102": sum(int(row["surface_count"]) for row in renderers) == 102,
        "variable_29": sum(int(row["surface_count"]) > 1 for row in renderers) == 29,
        "fixed_27": sum(int(row["surface_count"]) == 1 for row in renderers) == 27,
        "alternate_68": sum(row["surface_relation"] == "LICENSED_LOCAL_ALTERNATE" for row in events) == 68,
        "meaning_unchanged": all(row["meaning_unchanged"] == "YES" for row in events),
        "six_drills": len(drills) == 6 and sum(int(row["total_marks"]) for row in drills) == 438,
        "prose_partition": sum(int(row["portable_core_marks"]) + int(row["local_prose_model_marks"]) for row in drills) == 365,
        "condition_73": sum(int(row["condition_groups_to_copy"]) for row in drills) == 73,
        "switch_10": sum(int(row["owner_switch_checks"]) for row in drills) == 10,
        "five_checks": len(checks_table) == 5,
        "four_hands": len(hands) == 4,
        "no_empty": all(all(value for value in row.values()) for row in renderers + events + drills + checks_table + hands),
        "no_dictionary_change": summary["dictionary_changes"] == 0,
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
