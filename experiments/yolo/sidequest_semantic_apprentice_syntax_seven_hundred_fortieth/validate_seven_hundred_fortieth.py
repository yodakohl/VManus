#!/usr/bin/env python3
"""Validate Pass 740 apprentice syntax inventory."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_FORTIETH_39_COMPONENT_SLOT_MAP.tsv")
    patterns = read("SEVEN_HUNDRED_FORTIETH_116_STATEMENT_PATTERNS.tsv")
    templates = read("SEVEN_HUNDRED_FORTIETH_8_TEACHING_TEMPLATES.tsv")
    exceptions = read("SEVEN_HUNDRED_FORTIETH_21_HEADER_OR_ELLIPSIS_CASES.tsv")
    registers = read("SEVEN_HUNDRED_FORTIETH_REGISTER_COMPARISON.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["template_id"] for row in patterns)
    checks = {
        "inventory_39_116_8_21_2": (len(components), len(patterns), len(templates), len(exceptions), len(registers)) == (39, 116, 8, 21, 2),
        "all_components_slotted": all(row["apprentice_slot"] in {"ACTION", "MEMORY", "ADDRESS", "MATERIAL", "GRADE", "REFERENT", "CLOSE"} for row in components),
        "template_counts_exact": counts == {"T1": 47, "T2": 26, "T3": 11, "T4": 5, "T5": 16, "T6": 4, "T7": 6, "T8": 1},
        "all_statements_unique": len({row["statement_id"] for row in patterns}) == 116,
        "all_381_cards_accounted": sum(int(row["cards"]) for row in patterns) == 381,
        "all_850_components_accounted": sum(int(row["components"]) for row in patterns) == 850,
        "action_address_ellipsis_counts": summary["action_leading_statements"] == 95 and summary["address_leading_statements"] == 15 and summary["elliptic_statements"] == 6,
        "memory_start_20": summary["memory_start_statements"] == 20,
        "all_89_closes_final": summary["closed_statements"] == 89 and all((row["endpoint"] == "CLOSED") == row["component_sequence"].endswith("DY") for row in patterns),
        "register_split_exact": {(row["register"], int(row["statements"]), int(row["cards"]), int(row["single_card_statements"]), int(row["closed_statements"])) for row in registers} == {("HERBAL", 19, 100, 1, 4), ("BIOLOGICAL", 97, 281, 43, 85)},
        "all_readings_and_owners_present": all(row["owner_noun_de"].strip() and row["clean_workshop_reading_de"].strip() for row in patterns),
        "fixed_pages_only": {row["page"] for row in patterns} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in [components, patterns, templates, exceptions, registers] for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTIETH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
