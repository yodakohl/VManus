#!/usr/bin/env python3
"""Validate the cross-section journeyman piece."""

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
    steps = rows("SIXTY_FIRST_16_STEP_JOURNEYMAN_TRACE.tsv")
    bridges = rows("SIXTY_FIRST_4_EXTERNAL_JOB_BRIDGES.tsv")
    hands = rows("SIXTY_FIRST_4_HAND_JOURNEYMAN_COPIES.tsv")
    criteria = rows("SIXTY_FIRST_12_POINT_MARKING_SHEET.tsv")
    stage_counts = Counter(row["stage"] for row in steps)
    checks = {
        "sixteen_steps": len(steps) == 16 and [int(row["job_step"]) for row in steps] == list(range(1, 17)),
        "stage_counts_4_8_4": stage_counts == Counter({"BIO_STATION_APPLICATION": 8, "HERBAL_PREPARATION": 4, "LOCAL_CELESTIAL_LOOKUP": 4}),
        "four_external_bridges": len(bridges) == 4 and all(row["manuscript_cross_reference_claimed"] == "NO" for row in bridges),
        "four_hand_copies": len(hands) == 4 and len({row["scribe_profile"] for row in hands}) == 4,
        "all_hand_orders_preserved": all(row["prose_atom_order_preserved"] == "YES" and row["astro_namespace_order_preserved"] == "YES" for row in hands),
        "twelve_point_sheet": len(criteria) == 12 and sum(int(row["points"]) for row in criteria) == 12,
        "no_textual_cross_section_claim": all(row["cross_section_link_encoded_in_text"] == "NO" for row in steps),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in steps + hands),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "stage_counts": dict(stage_counts)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
