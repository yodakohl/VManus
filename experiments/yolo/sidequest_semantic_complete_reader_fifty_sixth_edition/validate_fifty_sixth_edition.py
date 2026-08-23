#!/usr/bin/env python3
"""Validate the complete pocket-grammar reader."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = rows("FIFTY_SIXTH_776_GROUP_READER.tsv")
    units = rows("FIFTY_SIXTH_258_COMPLETE_UNITS.tsv")
    deps = rows("FIFTY_SIXTH_258_CONTEXT_DEPENDENCIES.tsv")
    pages = rows("FIFTY_SIXTH_10_PAGE_SUMMARY.tsv")
    kind_counts = Counter(row["unit_kind"] for row in units)
    checks = {
        "exactly_776_groups": len(groups) == 776 and len({row["unified_serial"] for row in groups}) == 776,
        "exactly_258_units": len(units) == 258 and len({row["unit_id"] for row in units}) == 258,
        "exactly_258_dependency_rows": len(deps) == 258 and {row["unit_id"] for row in deps} == {row["unit_id"] for row in units},
        "ten_fixed_pages": len(pages) == 10 and {row["page"] for row in pages} == PAGES,
        "prose_116_astro_142": kind_counts == Counter({"ASTRO_LOCUS": 142, "PROSE_STATEMENT": 116}),
        "unit_group_sum_776": sum(int(row["group_count"]) for row in units) == 776,
        "page_group_sum_776": sum(int(row["visible_groups"]) for row in pages) == 776,
        "all_units_have_card_and_fluent_reading": all(row["card_by_card_reading_de"].strip() and row["fluent_working_reading_de"].strip() for row in units),
        "all_pocket_sequences_readable": all(row["pocket_sequence_readable"] == "YES" for row in units),
        "context_not_mislabeled_word": all(row["is_this_a_word_meaning"] == "NO_CONTEXT_LAYER" for row in deps),
        "no_line_end_assumption": all(row["sentence_ends_at_physical_line"] == "NO_ASSUMPTION" for row in units),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in groups + units),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "unit_kind_counts": dict(kind_counts)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
