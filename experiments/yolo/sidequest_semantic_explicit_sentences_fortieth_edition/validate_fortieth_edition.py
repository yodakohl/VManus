#!/usr/bin/env python3
"""Consistency checks for the fully explicit apprentice sentences."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows = read("FORTIETH_116_EXPLICIT_SENTENCES.tsv")
    checks = {
        "statements_116": len(rows) == 116,
        "ids_unique": len({row["statement_id"] for row in rows}) == 116,
        "sequences_complete": [int(row["sequence"]) for row in rows] == list(range(1, 117)),
        "records_11": len({row["record_id"] for row in rows}) == 11,
        "groups_381": sum(len(row["surface_sequence"].split()) for row in rows) == 381,
        "every_sentence_explicit": all(row["fully_explicit_apprentice_sentence_de"] for row in rows),
        "every_sentence_has_owner": all("OWNER" in row["memory_values_restored"].split("|") for row in rows),
        "all_literals_present": all(row["literal_visible_reading_de"] for row in rows),
        "all_macros_present": all(row["macro_program"] for row in rows),
        "record_book_exists": (OUT / "FORTIETH_11_EXPLICIT_RECORDS.md").exists(),
        "guide_exists": (OUT / "FORTIETH_EXPANSION_GUIDE.md").exists(),
        "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
