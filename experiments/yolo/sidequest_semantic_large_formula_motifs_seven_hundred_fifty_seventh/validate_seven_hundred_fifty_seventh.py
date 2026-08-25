#!/usr/bin/env python3
"""Validate Pass 757 large-formula motifs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    formulas = read("SEVEN_HUNDRED_FIFTY_SEVENTH_7_LARGE_FORMULAS.tsv")
    motifs = read("SEVEN_HUNDRED_FIFTY_SEVENTH_8_SHARED_CARD_MOTIFS.tsv")
    components = read("SEVEN_HUNDRED_FIFTY_SEVENTH_22_SHARED_COMPONENT_AXES.tsv")
    families = read("SEVEN_HUNDRED_FIFTY_SEVENTH_3_FORMULA_FAMILIES.tsv")
    gaps = read("SEVEN_HUNDRED_FIFTY_SEVENTH_14_COMPONENT_GAPS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FIFTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_7_8_22_3_14": (len(formulas), len(motifs), len(components), len(families), len(gaps)) == (7, 8, 22, 3, 14),
        "cards_58_to_74": (sum(int(row["predicted_cards"]) for row in formulas), sum(int(row["observed_cards"]) for row in formulas)) == (58, 74),
        "shared_31_local_43": (sum(int(row["shared_card_positions"]) for row in formulas), sum(int(row["formula_local_card_positions"]) for row in formulas)) == (31, 43),
        "family_partition_3_1_3": sorted(int(row["statements"]) for row in families) == [1, 3, 3],
        "y_aiin_all_seven": {row["component"]: row["formula_statements"] for row in components}.get("Y") == "7" and {row["component"]: row["formula_statements"] for row in components}.get("AIIN") == "7",
        "missing_36_extra_2": (sum(int(row["missing_occurrences"]) for row in gaps), sum(int(row["extra_occurrences"]) for row in gaps)) == (36, 2),
        "fixed_pages_only": {row["page"] for row in formulas} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (formulas, motifs, components, families, gaps) for row in rows),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIFTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
