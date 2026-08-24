#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("THREE_HUNDRED_SEVENTY_SIXTH_14_SOURCE_CARDS.tsv")
    visible = read("THREE_HUNDRED_SEVENTY_SIXTH_15_VISIBLE_FORMS.tsv")
    regions = read("THREE_HUNDRED_SEVENTY_SIXTH_PAGE_REGIONS.tsv")
    checks = {
        "14_cards": len(cards) == 14 and [int(r["source_position"]) for r in cards] == list(range(1, 15)),
        "all_cards_registered": all(r["surface_registered"] == r["value_matches_phrase"] == "YES" for r in cards),
        "four_cycles": len({r["microcycle"] for r in cards}) == 4,
        "two_owners": len({r["visible_owner"] for r in cards}) == 2,
        "15_visible": len(visible) == 15 and sum(int(r["source_contribution"]) for r in visible) == 14,
        "one_marked_carry": sum(r["visibility_role"] == "MARKED_ANTICIPATION" for r in visible) == 1,
        "five_lines": len({r["line_no"] for r in visible}) == 5,
        "images_first": [r["region_type"] for r in sorted(regions, key=lambda r: int(r["production_order"]))[:2]] == ["IMAGE", "IMAGE"],
        "two_images_four_text_regions": sum(r["region_type"] == "IMAGE" for r in regions) == 2 and sum(r["region_type"] == "TEXT" for r in regions) == 4,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_SIXTH_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
