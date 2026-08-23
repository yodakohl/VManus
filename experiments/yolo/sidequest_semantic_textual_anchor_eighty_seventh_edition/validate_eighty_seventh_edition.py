#!/usr/bin/env python3
"""Validate the eighty-seventh anchor/provenance edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    words = rows("EIGHTY_SEVENTH_44_WORD_ANCHOR_AUDIT.tsv")
    binding = rows("EIGHTY_SEVENTH_776_WORD_PROVENANCE_BINDING.tsv")
    weak = rows("EIGHTY_SEVENTH_MASTER_ONLY_WORDS.tsv")
    checks = {
        "word_count_44": len(words) == 44,
        "word_ids_unique": len({row["codex_word_id"] for row in words}) == 44,
        "binding_count_776": len(binding) == 776,
        "binding_serial_complete": [int(row["unified_serial"]) for row in binding] == list(range(1, 777)),
        "all_units_have_words": all(row["unit_program_word_ids"] for row in binding),
        "all_rows_warn_unit_program": all(row["provenance_warning"] == "UNIT_PROGRAM_NOT_ONE_WORD_PER_VISIBLE_GROUP" for row in binding),
        "four_anchor_classes": set(row["primary_anchor"] for row in words) == {
            "RECURRING_CARD_ANCHORED", "VISIBLE_OWNER_ANCHORED", "LOCAL_NOMENCLATOR_ONLY", "MASTER_PROGRAM_ONLY"
        },
        "weak_table_exact": {row["codex_word_id"] for row in weak} == {
            row["codex_word_id"] for row in words if row["primary_anchor"] == "MASTER_PROGRAM_ONLY"
        },
        "fixed_pages_only": set(row["page"] for row in binding) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in words + binding),
    }
    counts = Counter(row["primary_anchor"] for row in words)
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "anchor_counts": dict(counts)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
