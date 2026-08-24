#!/usr/bin/env python3
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
    drills = read("THREE_HUNDRED_EIGHTY_FIRST_SIX_SUBSTITUTION_DRILLS.tsv")
    cards = read("THREE_HUNDRED_EIGHTY_FIRST_84_CARD_BACKREAD.tsv")
    counts = Counter(row["drill_id"] for row in cards)
    changes = Counter(row["drill_id"] for row in cards if row["surface_changed"] == "YES")
    value_sequences = {
        drill_id: tuple(row["atomic_backread_de"] for row in cards if row["drill_id"] == drill_id)
        for drill_id in counts
    }
    identity_sequences = {
        drill_id: tuple(row["identity_backread"] for row in cards if row["drill_id"] == drill_id)
        for drill_id in counts
    }
    checks = {
        "six_drills": len(drills) == 6,
        "eighty_four_cards": len(cards) == 84,
        "fourteen_each": set(counts.values()) == {14},
        "one_change_each": set(changes.values()) == {1},
        "expected_surfaces": {row["substitute_surface"] for row in drills} == {"or", "chy", "dy", "shy", "aiin", "daiin"},
        "all_registered": all(row["surface_is_registered"] == "YES" for row in cards),
        "one_value_sequence": len(set(value_sequences.values())) == 1,
        "one_identity_sequence": len(set(identity_sequences.values())) == 1,
        "positions_complete": all({int(row["source_position"]) for row in cards if row["drill_id"] == drill} == set(range(1, 15)) for drill in counts),
        "target_metadata_preserved": all(row["one_change_only"] == row["identity_preserved"] == row["value_preserved"] == "YES" for row in drills),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
