#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows = read("TWO_HUNDRED_EIGHTY_FIRST_116_FORMULA_ASSIGNMENTS.tsv")
    templates = read("TWO_HUNDRED_EIGHTY_FIRST_EIGHT_PROSE_FORMULAS.tsv")
    expected = {"FLOW_TRANSFER_PROCESS": 33, "SIMPLE_OR_ELLIPTIC_PROCESS": 30, "FULL_ADDRESS_PROCESS": 12, "SOURCED_PROCESS": 12, "GRADED_PROCESS": 11, "QUANTIFIED_PROCESS": 9, "TARGET_APPLICATION_PROCESS": 6, "LINKED_PROCESS": 3}
    checks = {
        "116_statements": len(rows) == 116,
        "eight_templates": len(templates) == 8,
        "counts_exact": Counter(r["formula_family"] for r in rows) == expected,
        "template_sum_116": sum(int(r["statement_count"]) for r in templates) == 116,
        "statement_ids_unique": len({r["statement_id"] for r in rows}) == 116,
        "eleven_records": len({r["record_unit_id"] for r in rows}) == 11,
        "all_fluent_nonempty": all(r["fluent_formula_reading_de"].strip() for r in rows),
        "all_family_sequences_nonempty": all(r["family_sequence_de"].strip() for r in rows),
        "open_closed_complete": Counter(r["terminal_status"] for r in rows) == {"CLOSED": 90, "OPEN": 26},
        "one_stale_close_corrected": [r["statement_id"] for r in rows if r["grammar_close_disagreement"] == "YES"] == ["H4-S002"],
        "only_allowed_pages": {r["page"] for r in rows} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in rows),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
