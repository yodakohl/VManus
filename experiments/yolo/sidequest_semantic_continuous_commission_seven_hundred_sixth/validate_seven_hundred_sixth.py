#!/usr/bin/env python3
"""Validate Pass 706 continuous commission."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    statements = read("SEVEN_HUNDRED_SIXTH_7_STATEMENT_COMMISSION.tsv")
    trace = read("SEVEN_HUNDRED_SIXTH_14_CARD_FORWARD_BACKWARD_TRACE.tsv")
    lines = read("SEVEN_HUNDRED_SIXTH_3_PHYSICAL_LINES.tsv")
    owners = read("SEVEN_HUNDRED_SIXTH_2_OWNER_STATES.tsv")
    checks = {
        "statements_7": len(statements) == 7,
        "cards_14": len(trace) == 14,
        "two_cards_per_statement": all(sum(row["statement_no"] == statement["statement_no"] for row in trace) == 2 for statement in statements),
        "all_templates_attested": all(int(row["role_template_support"]) >= 1 for row in statements),
        "physical_lines_3": len(lines) == 3,
        "line_cards_14": sum(len(row["surface_line"].split()) for row in lines) == 14,
        "line_wrap_not_sentence": all(row["line_boundary_rule"] == "PHYSICAL_WRAP_ONLY__NOT_SENTENCE_BOUNDARY" for row in lines),
        "owners_2": len(owners) == 2,
        "plant_then_basin": [row["owner_id"] for row in trace] == ["PLANT_OWNER"] * 8 + ["BASIN_STATION"] * 6,
        "two_closures": sum(row["ends_work_step"] == "YES" for row in statements) == 2,
        "no_new_cards": all(row["new_card"] == "NO" for row in trace),
        "no_new_surfaces": all(row["new_surface"] == "NO" for row in trace),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
