#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventh.py")], check=True)
    cards = read("EIGHT_HUNDRED_SEVENTH_19_MATERIAL_CARDS.tsv")
    events = read("EIGHT_HUNDRED_SEVENTH_30_MATERIAL_EVENTS.tsv")
    decisions = read("EIGHT_HUNDRED_SEVENTH_3_MATERIAL_ROOT_DECISIONS.tsv")
    stacks = read("EIGHT_HUNDRED_SEVENTH_MATERIAL_STACK.tsv")
    readings = read("EIGHT_HUNDRED_SEVENTH_5_READABLE_STATEMENTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_root = {row["component"]: row for row in decisions}
    checks = {
        "nineteen_cards_thirty_union_events": len(cards) == 19 and len(events) == 30,
        "component_event_sum_31": summary["component_event_sum"] == 31,
        "root_counts_air5_or18_ho8": (by_root["AIR"]["events"], by_root["OR"]["events"], by_root["HO"]["events"]) == ("5", "18", "8"),
        "all_meanings_invariant_promoted": all(row["meaning_invariant"] == "YES" and row["decision"] == "PROMOTE_TO_PARADIGM_CORE25" for row in decisions),
        "one_ho_or_stack": len(stacks) == 1 and stacks[0]["component_recipe"] == "HO+CH+OR",
        "five_readable_statements": len(readings) == 5,
        "core25_strip6": summary["new_core_size"] == 25 and summary["remaining_recurrent_strip_values"] == 6,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
