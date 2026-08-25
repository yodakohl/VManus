#!/usr/bin/env python3
"""Validate Pass 728 portable mini-grammar."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    templates = read("SEVEN_HUNDRED_TWENTY_EIGHTH_4_TEACHING_TEMPLATES.tsv")
    occurrences = read("SEVEN_HUNDRED_TWENTY_EIGHTH_16_TEMPLATE_OCCURRENCES.tsv")
    statements = read("SEVEN_HUNDRED_TWENTY_EIGHTH_116_STATEMENT_TEMPLATE_EDITION.tsv")
    records = read("SEVEN_HUNDRED_TWENTY_EIGHTH_11_RECORD_TEMPLATE_SUMMARY.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_TWENTY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = {row["card_pair"]: sum(item["card_pair"] == row["card_pair"] for item in occurrences) for row in occurrences}
    checks = {
        "templates_four": [row["template_id"] for row in templates] == ["PT1", "PT2", "PT3", "PT4"],
        "occurrences_16_unique": len(occurrences) == 16 and len({row["occurrence_id"] for row in occurrences}) == 16,
        "six_bigram_counts": counts == {"PROC008>PROC009": 2, "PROC009>PROC019": 3, "PROC013>PROC009": 2, "PROC016>PROC019": 3, "PROC019>PROC009": 4, "PROC022>PROC013": 2},
        "register_split_8_8": sum(row["register"] == "HERBAL_WHAT" for row in occurrences) == 8 and sum(row["register"] == "BIOLOGICAL_HOW" for row in occurrences) == 8,
        "statements_116_events_381": len(statements) == 116 and sum(int(row["events"]) for row in statements) == 381,
        "records_11": [row["record"] for row in records] == ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"],
        "records_using_templates_9": sum(int(row["portable_template_occurrences"]) > 0 for row in records) == 9,
        "all_occurrences_no_pointer": all(row["direct_cross_reference"] == "NONE" for row in occurrences),
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in statements),
        "old_equal_parts_revised": summary["revised_old_y_aiin_y_gloss"] == "FROM_EQUAL_PARTS_TO_CURRENT_ITEM_MEASURE_BRACKET",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
