#!/usr/bin/env python3
"""Validate complete layered H3 and B2 readbacks."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = read_tsv("SEVENTY_THIRD_79_GROUP_LAYERED_READINGS.tsv")
    statements = read_tsv("SEVENTY_THIRD_26_LAYERED_STATEMENTS.tsv")
    records = read_tsv("SEVENTY_THIRD_2_COMPLETE_LAYERED_PASSAGES.tsv")
    checks = {
        "seventy_nine_groups": len(groups) == 79 and len({row["source_group_id"] for row in groups}) == 79,
        "group_partition": sum(row["record_id"] == "H3" for row in groups) == 17 and sum(row["record_id"] == "B2" for row in groups) == 62,
        "twenty_six_statements": len(statements) == 26 and len({row["unit_id"] for row in statements}) == 26,
        "statement_partition": sum(row["record_id"] == "H3" for row in statements) == 4 and sum(row["record_id"] == "B2" for row in statements) == 22,
        "two_records": len(records) == 2 and {row["record_id"] for row in records} == {"H3", "B2"},
        "all_layers_present": all(all(row[key] for key in ("surface_sequence", "minimal_dictionary_reading", "owner_augmented_reading", "neutral_source_formular", "medical_master_expansion", "nonmedical_master_expansion")) for row in statements),
        "cards_and_owners_unchanged": all(row["card_or_owner_changed_between_master_expansions"] == "NO" for row in statements),
        "pages_only_f11r_f82r": {row["page"] for row in groups + statements + records} == {"f11r", "f82r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in groups + statements + records),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
