#!/usr/bin/env python3
"""Validate owner hierarchy over ambiguous case fragments."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    contexts = read("SIX_HUNDRED_FORTY_SEVENTH_74_OWNER_CONTEXTS.tsv")
    levels = read("SIX_HUNDRED_FORTY_SEVENTH_12_LEVEL_SUMMARY.tsv")
    minimum = read("SIX_HUNDRED_FORTY_SEVENTH_4_MINIMUM_LEVELS.tsv")
    checks = {
        "seventy_four_contexts": len(contexts) == 74,
        "two_contexts_each_fragment": len({row["fragment_id"] for row in contexts}) == 37 and all(sum(item["fragment_id"] == row["fragment_id"] for item in contexts) == 2 for row in contexts),
        "herbal_and_bio_balanced": sum(row["domain"] == "HERBAL" for row in contexts) == 37 and sum(row["domain"] == "BIOLOGICAL" for row in contexts) == 37,
        "twelve_level_rows": len(levels) == 12,
        "desk_resolves_twenty_four": sum(row["desk_resolves"] == "YES" for row in contexts) == 24,
        "page_resolves_sixty_one": sum(row["page_resolves"] == "YES" for row in contexts) == 61,
        "record_resolves_all": all(row["record_resolves"] == "YES" and row["record_candidate_count"] == "1" for row in contexts),
        "thirteen_need_record": sum(row["minimum_context_level"] == "RECORD" for row in contexts) == 13,
        "no_unresolved": sum(row["minimum_context_level"] == "UNRESOLVED" for row in contexts) == 0,
        "no_automatic_insertions": all(row["may_insert_missing_cards"] == "NO_NOT_UNLESS_COPY_DAMAGE_IS_INDEPENDENTLY_KNOWN" for row in contexts),
        "four_minimum_rows": len(minimum) == 4,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
