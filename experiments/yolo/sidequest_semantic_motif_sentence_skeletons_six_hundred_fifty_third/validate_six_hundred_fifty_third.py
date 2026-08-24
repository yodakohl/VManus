#!/usr/bin/env python3
"""Validate the 25 source role skeletons."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    skeletons = rows("SIX_HUNDRED_FIFTY_THIRD_25_SOURCE_ROLE_SKELETONS.tsv")
    rules = rows("SIX_HUNDRED_FIFTY_THIRD_8_APPRENTICE_RULES.tsv")
    patterns = rows("SIX_HUNDRED_FIFTY_THIRD_13_COARSE_PATTERNS.tsv")
    checks = {
        "twenty_five_skeletons": len(skeletons) == 25,
        "one_hundred_fifty_eight_events": sum(int(row["event_count"]) for row in skeletons) == 158,
        "fifty_eight_motif_events": sum(int(row["motif_events"]) for row in skeletons) == 58,
        "one_hundred_local_events": sum(int(row["local_events"]) for row in skeletons) == 100,
        "eight_rules": len(rules) == 8,
        "thirteen_coarse_patterns": len(patterns) == 13,
        "twenty_four_counted_motif_patterns": len({row["counted_skeleton"] for row in skeletons}) == 24,
        "twenty_five_exact_recipes": len({row["exact_workshop_recipe"] for row in skeletons}) == 25,
        "all_exact_roundtrips": all(row["exact_roundtrip"] == "YES" for row in skeletons),
        "cards_roundtrip": all(row["source_cards"] == row["reconstructed_cards"] for row in skeletons),
        "surfaces_roundtrip": all(row["source_surface"] == row["reconstructed_surface"] for row in skeletons),
        "close_only_final": all("CLOSE>" not in row["coarse_skeleton"] for row in skeletons),
        "binder_has_right_local": all(
            all(i + 1 < len(parts) and parts[i + 1] == "LOCAL" for i, part in enumerate(parts) if part == "BINDER")
            for parts in (row["coarse_skeleton"].split(">") for row in skeletons)
        ),
        "bridge_has_local_both_sides": all(
            all(i > 0 and i + 1 < len(parts) and parts[i - 1] == "LOCAL" and parts[i + 1] == "LOCAL" for i, part in enumerate(parts) if part == "BRIDGE")
            for parts in (row["coarse_skeleton"].split(">") for row in skeletons)
        ),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
