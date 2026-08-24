#!/usr/bin/env python3
"""Validate the compressed local exception deck."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    causes = read("SIX_HUNDRED_TWENTY_NINTH_21_EXCEPTION_CAUSES.tsv")
    deck = read("SIX_HUNDRED_TWENTY_NINTH_16_MEMORIZED_SURFACE_ENTRIES.tsv")
    resolved = read("SIX_HUNDRED_TWENTY_NINTH_3_ADDITIONAL_RULE_RESOLUTIONS.tsv")
    writer = read("SIX_HUNDRED_TWENTY_NINTH_372_REVISED_SURFACE_WRITER.tsv")
    statuses = Counter(row["resolution_status"] for row in causes)
    checks = {
        "causes21": len(causes) == 21 and len({row["event_id"] for row in causes}) == 21,
        "status_counts": statuses == {"RESOLVED_COMPACT_RULE": 3, "GROUPED_PHRASE": 3, "KEEP_LOCAL": 15},
        "resolved_exact_three": {row["event_id"] for row in resolved} == {"E022", "E233", "E352"},
        "deck16": len(deck) == 16 and len({row["exception_entry"] for row in deck}) == 16,
        "deck_covers18_events": sum(int(row["event_count"]) for row in deck) == 18,
        "b1_phrase_is_one_entry": next(row for row in deck if row["exception_entry"] == "X01_B1_KEEY_OL_SHED_CADENCE")["event_ids"] == "E153|E154|E155",
        "writer372": len(writer) == 372 and len({row["event_id"] for row in writer}) == 372,
        "all_roundtrip": all(row["revised_exact_roundtrip"] == "YES" for row in writer),
        "three_additional_rule_rows": sum(row["revised_surface_writer_layer"] == "ADDITIONAL_COMPACT_RULE" for row in writer) == 3,
        "eighteen_exception_events": sum(row["revised_surface_writer_layer"] == "SIXTEEN_ENTRY_LOCAL_EXCEPTION_DECK" for row in writer) == 18,
        "field_entry_count": sum(row["field_position"] in {"FIRST", "ONLY"} for row in causes) == 9,
        "post_close_entry_count": sum(row["post_close_field_entry"] == "YES" for row in causes) == 4,
        "no_sealed_pages": not any(row["page"].startswith("f84") for row in causes),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
