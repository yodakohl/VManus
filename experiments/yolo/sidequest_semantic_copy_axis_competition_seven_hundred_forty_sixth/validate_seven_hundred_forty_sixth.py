#!/usr/bin/env python3
"""Validate Pass 746 copy-axis competition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    decisions = read("SEVEN_HUNDRED_FORTY_SIXTH_4_AXIS_DECISIONS.tsv")
    audit = read("SEVEN_HUNDRED_FORTY_SIXTH_464_AXIS_AUDIT.tsv")
    inventory = read("SEVEN_HUNDRED_FORTY_SIXTH_4_AXIS_VALENCY_INVENTORY.tsv")
    harms = read("SEVEN_HUNDRED_FORTY_SIXTH_2_HARM_CASES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_SIXTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    lookup = {row["axis"]: row for row in decisions}
    checks = {
        "inventory_4_464_4_2": (len(decisions), len(audit), len(inventory), len(harms)) == (4, 464, 4, 2),
        "axes_exact": set(lookup) == {"OL", "AL", "AIIN", "OK"},
        "all_no_gain": all(int(row["newly_fixed"]) == 0 for row in decisions),
        "ol_no_harm": (int(lookup["OL"]["copied_axis_occurrences"]), int(lookup["OL"]["newly_harmed"]), int(lookup["OL"]["exact_recipe_sequences"])) == (3, 0, 84),
        "ok_no_harm": (int(lookup["OK"]["copied_axis_occurrences"]), int(lookup["OK"]["newly_harmed"]), int(lookup["OK"]["exact_recipe_sequences"])) == (1, 0, 84),
        "al_harms_b2s006": int(lookup["AL"]["copied_axis_occurrences"]) == 4 and lookup["AL"]["newly_harmed_ids"] == "B2-S006" and int(lookup["AL"]["exact_recipe_sequences"]) == 83,
        "aiin_harms_b1s014": int(lookup["AIIN"]["copied_axis_occurrences"]) == 1 and lookup["AIIN"]["newly_harmed_ids"] == "B1-S014" and int(lookup["AIIN"]["exact_recipe_sequences"]) == 83,
        "retain_none": all(row["retain_rule"] == "NO" for row in decisions) and summary["retained_axes"] == [],
        "all_116_per_axis": all(sum(row["axis"] == axis for row in audit) == 116 for axis in {"OL", "AL", "AIIN", "OK"}),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in [decisions, audit, inventory, harms] for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
