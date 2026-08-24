#!/usr/bin/env python3
"""Validate the twelve-card master tablet."""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    tablet = read_tsv("THREE_HUNDRED_FIFTY_FIRST_TWELVE_CARD_MASTER_TABLET.tsv")
    strips = read_tsv("THREE_HUNDRED_FIFTY_FIRST_TWELVE_CONTEXT_STRIPS.tsv")
    checks = {
        "twelve_cards": len(tablet) == 12,
        "twelve_distinct_events": len({row["event_id"] for row in tablet}) == 12,
        "twelve_distinct_tuples": len({row["joint_tuple_id"] for row in tablet}) == 12,
        "twelve_context_strips": len(strips) == 12,
        "tablet_ids_match": {row["tablet_no"] for row in tablet} == {row["tablet_no"] for row in strips},
        "all_whole_cards": all(row["must_remain_whole_card"] == "YES" for row in tablet),
        "all_concrete_values": all(row["concrete_work_value_de"] and row["concrete_work_value_de"] not in {"UNKNOWN", "FORMAL"} for row in tablet),
        "all_have_owner": all(row["picture_or_station_owner"] for row in tablet),
        "all_have_mnemonic": all(row["master_mnemonic_de"] for row in tablet),
        "all_have_distinct_contrast": all(row["whole_card_surface"] != row["nearest_contrast_surface"] and row["concrete_work_value_de"] != row["nearest_contrast_value_de"] for row in tablet),
        "target_marked_once": all(row["surface_strip"].count("[") == 1 and row["surface_strip"].count("]") == 1 for row in strips),
        "fixed_pages_only": {row["page"] for row in tablet} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
