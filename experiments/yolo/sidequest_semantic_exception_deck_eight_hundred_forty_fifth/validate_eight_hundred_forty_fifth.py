#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_FIFTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_fifth.py")], check=True)
    cards = read("6_EXCEPTION_CARDS.tsv")
    events = read("7_EXCEPTION_EVENTS.tsv")
    lessons = read("6_APPRENTICE_EXCEPTION_LESSONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "exception_inventory": len(cards) == 6 and len(events) == 7 and len(lessons) == 6,
        "identity_counts": len({row["exact_card_id"] for row in cards}) == 6 and len({row["event_id"] for row in events}) == 7,
        "mode_split": sum(row["learning_mode"] == "MEMORIZE_BOUND_FRAME" for row in cards) == 3 and sum(row["learning_mode"] == "MEMORIZE_WHOLE_CARD" for row in cards) == 3,
        "whole_values": {row["short_invariant_value_de"] for row in cards if row["learning_mode"] == "MEMORIZE_WHOLE_CARD"} == {"DAZU", "DAVON", "BEISEITESTELLEN"},
        "bound_values": {row["component_recipe"] for row in cards if row["learning_mode"] == "MEMORIZE_BOUND_FRAME"} == {"Y+K+AN", "OK+Y+LD+DY", "DA+IIN"},
        "event_values_constant": all(row["same_value_as_card"] == "YES" for row in events),
        "full_inventory_accounting": summary["fully_composed_cards"] == 167 and summary["fully_composed_events"] == 374 and summary["exception_cards"] == 6 and summary["exception_events"] == 7,
        "lesson_boundaries": all(row["do_not_generalize"] and row["practice"] for row in lessons),
        "allowed_pages": {row["page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
