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
    cards = read("THREE_HUNDRED_SEVENTIETH_SIXTEEN_RENDERED_CARDS.tsv")
    cross = read("THREE_HUNDRED_SEVENTIETH_FOUR_CROSS_READS.tsv")
    checks = {
        "sixteen_cards": len(cards) == 16,
        "two_palettes": len({r["palette_id"] for r in cards}) == 2,
        "eight_per_palette": all(sum(r["palette_id"] == p for r in cards) == 8 for p in {r["palette_id"] for r in cards}),
        "all_registered": all(r["registered_for_card"] == "YES" for r in cards),
        "all_surface_unique": all(r["surface_decodes_uniquely"] == "YES" for r in cards),
        "three_pairs_each": all(sum(r["palette_id"] == p and r["pair_id"] != "NONE" for r in cards) == 3 for p in {r["palette_id"] for r in cards}),
        "four_crossreads": len(cross) == 4 and all(r["full_crossread"] == "YES" for r in cross),
        "all_layers_match": all(r["identities_match"] == r["values_match"] == r["pair_decisions_match"] == "YES" for r in cross),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
