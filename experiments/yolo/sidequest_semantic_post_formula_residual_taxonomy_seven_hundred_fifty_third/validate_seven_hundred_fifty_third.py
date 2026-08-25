#!/usr/bin/env python3
"""Validate Pass 753 residual taxonomy."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    taxonomy = read("SEVEN_HUNDRED_FIFTY_THIRD_19_RESIDUAL_TAXONOMY.tsv")
    classes = read("SEVEN_HUNDRED_FIFTY_THIRD_4_CLASS_SUMMARY.tsv")
    minimal = read("SEVEN_HUNDRED_FIFTY_THIRD_7_MINIMAL_NEXT_CASES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FIFTY_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = {row["residual_class"]: int(row["statements"]) for row in classes}
    checks = {
        "counts_19_4_7": (len(taxonomy), len(classes), len(minimal)) == (19, 4, 7),
        "class_partition_7_2_3_7": counts == {"MINIMAL_SINGLE_CHANGE": 7, "SEGMENTATION_OR_REDISTRIBUTION": 2, "SMALL_PHRASE_REORDER": 3, "LARGE_LEARNED_FORMULA": 7},
        "unique_statements": len({row["statement_id"] for row in taxonomy}) == 19,
        "minimal_edit_distance_one": all(row["card_edit_distance"] == "1" for row in minimal),
        "minimal_priority_now": all(row["next_priority"] == "NOW" for row in minimal),
        "fixed_pages_only": {row["page"] for row in taxonomy} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (taxonomy, classes, minimal) for row in rows),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIFTY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
