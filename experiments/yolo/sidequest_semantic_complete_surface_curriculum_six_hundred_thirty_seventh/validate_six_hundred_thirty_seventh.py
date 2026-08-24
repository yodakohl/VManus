#!/usr/bin/env python3
"""Validate the all-prose apprentice curriculum."""

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
    c6 = read("SIX_HUNDRED_THIRTY_SEVENTH_9_C6_SURFACE_WRITER.tsv")
    full = read("SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    deck = read("SIX_HUNDRED_THIRTY_SEVENTH_17_SURFACE_EXCEPTION_ENTRIES.tsv")
    layers = Counter(row["surface_writer_layer"] for row in full)
    checks = {
        "nine_c6_events": len(c6) == 9 and {row["event_id"] for row in c6} == {f"E{i}" for i in range(373, 382)},
        "c6_five_three_one": sum(row["final_surface_writer_layer"] == "SEMANTIC_CARD_OR_DESK_RULE" for row in c6) == 5 and sum(row["final_surface_writer_layer"] == "TWO_STAGE_BODY_WRAPPER_RULE" for row in c6) == 3 and sum(row["final_surface_writer_layer"] == "SEVENTEEN_ENTRY_LOCAL_EXCEPTION_DECK" for row in c6) == 1,
        "c6_exception_is_e377": {row["event_id"] for row in c6 if row["compact_exception_entry"] != "NONE"} == {"E377"},
        "three_hundred_eighty_one_events": len(full) == 381 and [row["event_id"] for row in full] == [f"E{i:03d}" for i in range(1, 382)],
        "layer_counts_198_161_3_18_1": layers == Counter({"SEMANTIC_CARD_OR_DESK_RULE": 198, "TWO_STAGE_BODY_WRAPPER_RULE": 161, "SIXTEEN_ENTRY_LOCAL_EXCEPTION_DECK": 18, "ADDITIONAL_COMPACT_RULE": 3, "SEVENTEEN_ENTRY_LOCAL_EXCEPTION_DECK": 1}),
        "seventeen_entries_nineteen_events": len(deck) == 17 and sum(int(row["event_count"]) for row in deck) == 19,
        "all_exact_roundtrip": all(row["exact_roundtrip"] == "YES" and row["predicted_surface"] == row["surface"] for row in full),
        "four_semantic_classes": len({row["semantic_burden_class"] for row in full}) == 4,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
