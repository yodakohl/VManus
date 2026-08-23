#!/usr/bin/env python3
"""Validate the source-formular skeleton."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    assignments = rows("SIXTY_SECOND_381_SOURCE_SLOT_ASSIGNMENTS.tsv")
    formulars = rows("SIXTY_SECOND_116_DUAL_SOURCE_FORMULARS.tsv")
    rules = rows("SIXTY_SECOND_10_SOURCE_SLOT_RULES.tsv")
    checks = {
        "all_381_prose_groups": len(assignments) == 381 and len({row["source_group_id"] for row in assignments}) == 381,
        "all_116_formulars": len(formulars) == 116 and len({row["unit_id"] for row in formulars}) == 116,
        "ten_slot_rules": len(rules) == 10 and len({row["source_slot"] for row in rules}) == 10,
        "group_sum_381": sum(int(row["group_count"]) for row in formulars) == 381,
        "all_groups_assigned": all(row["slot_assignment_complete"] == "YES" and row["source_slot_sequence"] for row in assignments),
        "no_language_claim": all(row["source_language_claim"] == "NONE_TWO_ORDERING_STYLES_ONLY" for row in formulars),
        "no_sentence_specific_slot_rule": all(row["sentence_specific_slot_rule"] == "NO" for row in formulars),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in assignments + formulars),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
