#!/usr/bin/env python3
"""Consistency checks for the apprentice error book."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rules = read("FORTY_FIRST_EIGHT_ERROR_RULES.tsv")
    errors = read("FORTY_FIRST_32_APPRENTICE_ERRORS.tsv")
    checks = {
        "eight_rules": len(rules) == 8,
        "rule_codes_unique": len({row["error_code"] for row in rules}) == 8,
        "thirty_two_errors": len(errors) == 32,
        "four_per_rule": all(sum(row["error_code"] == rule["error_code"] for row in errors) == 4 for rule in rules),
        "statements_distinct": len({row["statement_id"] for row in errors}) == 32,
        "records_diverse": len({row["record_id"] for row in errors}) >= 8,
        "pages_diverse": len({row["page"] for row in errors}) == 7,
        "every_wrong_differs": all(row["wrong_atom_or_register_reading"] != row["correct_atom_sequence"] or row["error_code"] in {"E01_WRONG_OWNER", "E02_ACTIVE_PREVIOUS_SWAP"} for row in errors),
        "every_repair_present": all(row["repair_rule_de"] for row in errors),
        "every_full_sentence_present": all(row["correct_full_sentence_de"] for row in errors),
        "copybook_exists": (OUT / "FORTY_FIRST_CORRECTION_COPYBOOK.md").exists(),
        "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in errors),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
