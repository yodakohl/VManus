#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_FIRST"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_first.py")], check=True)
    lesson = read(f"{PREFIX}_7_RULE_LESSON.tsv")
    assignments = read(f"{PREFIX}_692_CARD_ASSIGNMENTS.tsv")
    matrix = read(f"{PREFIX}_173_CARD_MATRIX.tsv")
    extras = read(f"{PREFIX}_10_EXTRA_VARIANTS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    cards = {row["exact_card_id"] for row in matrix}
    checks = {
        "inventory": len(lesson) == 7 and len(matrix) == 173 and len(assignments) == 692 and len(extras) == 10,
        "four_per_card": all(sum(row["exact_card_id"] == card for row in assignments) == 4 for card in cards),
        "registered": all(row["registered"] == "YES" for row in assignments),
        "same_meaning": all(row["same_card_and_meaning"] == "YES" for row in assignments),
        "mixed_inventory": summary["fixed_surface_cards"] == 139 and summary["multi_surface_cards"] == 34 and summary["profile_sensitive_cards"] == 33,
        "variant_accounting": summary["registered_card_surface_pairs"] == 230 and summary["selected_distinct_card_surface_pairs"] == 220 and summary["unselected_extra_variants"] == 10,
        "coverage": summary["coverage_percent"] == 95.7,
        "no_semantic_disagreement": summary["semantic_disagreements"] == 0,
        "no_hand_attribution": summary["actual_hand_attributions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
