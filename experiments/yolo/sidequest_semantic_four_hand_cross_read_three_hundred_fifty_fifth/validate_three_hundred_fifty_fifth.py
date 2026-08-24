#!/usr/bin/env python3
"""Validate four-hand rendering and cross-reading."""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    renderings = read_tsv("THREE_HUNDRED_FIFTY_FIFTH_FORTY_FOUR_HAND_RENDERINGS.tsv")
    matrix = read_tsv("THREE_HUNDRED_FIFTY_FIFTH_SIXTEEN_CROSS_READS.tsv")
    variants = read_tsv("THREE_HUNDRED_FIFTY_FIFTH_ELEVEN_SURFACE_VARIANTS.tsv")
    checks = {
        "forty_four_renderings": len(renderings) == 44,
        "four_hands": len({row["source_hand"] for row in renderings}) == 4,
        "eleven_per_hand": all(sum(row["source_hand"] == hand for row in renderings) == 11 for hand in {row["source_hand"] for row in renderings}),
        "all_renderings_decode": all(row["joint_tuple_id"] == row["decoded_joint_tuple_id"] and row["identity_value_slot_state_preserved"] == "YES" for row in renderings),
        "sixteen_cross_reads": len(matrix) == 16,
        "all_hand_pairs": len({(row["source_hand"], row["reader_hand"]) for row in matrix}) == 16,
        "all_cross_reads_11_of_11": all(row["cards_read"] == "11" and row["identity_matches"] == "11" for row in matrix),
        "all_roundtrip": all(row["full_roundtrip"] == "YES" and row["values_match"] == "YES" and row["slots_match"] == "YES" and row["material_thread_matches"] == "YES" for row in matrix),
        "eleven_variant_rows": len(variants) == 11,
        "six_variable_five_invariant": sum(row["surface_behavior"] == "HAND_VARIABLE" for row in variants) == 6 and sum(row["surface_behavior"] == "INVARIANT" for row in variants) == 5,
        "four_distinct_complete_sequences": len({row["source_surface_sequence"] for row in matrix}) == 4,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
