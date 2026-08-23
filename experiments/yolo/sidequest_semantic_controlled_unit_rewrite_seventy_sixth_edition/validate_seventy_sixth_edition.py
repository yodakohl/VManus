#!/usr/bin/env python3
"""Validate the bounded fourteen-unit controlled rewrite."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    units = read_tsv("SEVENTY_SIXTH_14_CONTROLLED_UNIT_READINGS.tsv")
    bindings = read_tsv("SEVENTY_SIXTH_776_CONTROLLED_REWRITE_BINDING.tsv")
    manual = read_tsv("SEVENTY_SIXTH_8_RULE_CONTROLLED_WRITING_MANUAL.tsv")
    checks = {
        "fourteen_units": len(units) == 14 and len({row["unit_id"] for row in units}) == 14,
        "ten_pages": len({row["page"] for row in units}) == 10,
        "register_split": sum(row["unit_id"].startswith("H") for row in units) == 5 and sum(row["unit_id"].startswith("B") for row in units) == 6 and sum(row["unit_id"].startswith("A") for row in units) == 3,
        "all_units_readable": all(row["controlled_unit_reading_de"] and row["one_sentence_compression_de"] for row in units),
        "no_free_noun_flags": all(row["free_content_nouns_added"] == "NONE" for row in units),
        "group_total": sum(int(row["group_count"]) for row in units) == 776,
        "776_bindings": len(bindings) == 776 and len({row["unified_serial"] for row in bindings}) == 776,
        "all_bindings_controlled": all(row["controlled_rewrite_status"] == "BOUND_WITHOUT_FREE_CONTENT_NOUN" for row in bindings),
        "eight_rules": len(manual) == 8,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in units + bindings + manual),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
