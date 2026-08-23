#!/usr/bin/env python3
"""Consistency checker for process macros."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    macros = read("THIRTY_EIGHTH_20_PROCESS_MACROS.tsv")
    programs = read("THIRTY_EIGHTH_116_MACRO_PROGRAMS.tsv")
    worked = read("THIRTY_EIGHTH_WORKED_JOB_MACRO_PROGRAM.tsv")
    checks = {
        "twenty_macros": len(macros) == 20,
        "macro_ids_unique": len({r["macro_id"] for r in macros}) == 20,
        "all_macros_recur": all(int(r["raw_occurrence_count"]) >= 2 for r in macros),
        "all_macros_cross_record": all(int(r["raw_record_count"]) >= 2 for r in macros),
        "statements_116": len(programs) == 116,
        "clauses_254": sum(int(r["clause_count"]) for r in programs) == 254,
        "reconstruction_exact": all(r["clause_family_sequence"] == r["reconstructed_clause_family_sequence"] for r in programs),
        "token_counts_valid": all(int(r["macro_token_count"]) <= int(r["clause_count"]) for r in programs),
        "worked_statements_26": len(worked) == 26,
        "worked_ids_unique": len({r["statement_id"] for r in worked}) == 26,
        "macro_level_explicit": all(r["semantic_level"] == "PROCESS_MACRO_ABOVE_CARD_LEVEL" for r in macros),
        "word_prohibition": all(r["word_meaning_prohibition"].startswith("NEVER_ASSIGN") for r in macros),
        "macro_book": (OUT / "THIRTY_EIGHTH_WORKSHOP_MACRO_BOOK.md").exists(),
        "report": (OUT / "THIRTY_EIGHTH_EDITION_REPORT.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
