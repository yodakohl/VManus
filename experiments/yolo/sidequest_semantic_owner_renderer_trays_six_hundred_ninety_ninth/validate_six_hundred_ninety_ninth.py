#!/usr/bin/env python3
"""Validate owner trays and local override slips."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_ninth.py")], check=True)
    trays = read("SIX_HUNDRED_NINETY_NINTH_18_OWNER_TRAYS.tsv")
    defaults = read("SIX_HUNDRED_NINETY_NINTH_49_OWNER_CARD_DEFAULTS.tsv")
    conflicts = read("SIX_HUNDRED_NINETY_NINTH_4_CONFLICT_PAIRS.tsv")
    overrides = read("SIX_HUNDRED_NINETY_NINTH_5_LOCAL_OVERRIDE_SLIPS.tsv")
    events = read("SIX_HUNDRED_NINETY_NINTH_59_RESIDUAL_RECONSTRUCTIONS.tsv")
    checks = {
        "eighteen_trays": len(trays) == 18,
        "old_modes_thirty_four": sum(int(row["old_locus_modes_collapsed"]) for row in trays) == 34,
        "forty_nine_defaults": len(defaults) == 49 and len({(row["owner_de"], row["card_no"]) for row in defaults}) == 49,
        "four_conflicts": len(conflicts) == 4,
        "five_overrides": len(overrides) == 5 and len({row["event_id"] for row in overrides}) == 5,
        "forty_five_invariant_pairs": sum(row["owner_card_conflict"] == "NO" for row in defaults) == 45,
        "fifty_nine_events": len(events) == 59 and len({row["event_id"] for row in events}) == 59,
        "all_exact": all(row["reconstructed_surface"] == row["actual_surface"] and row["exact_match"] == "YES" for row in events),
        "override_events_align": {row["event_id"] for row in overrides} == {row["event_id"] for row in events if row["selection_source"] == "LOCAL_OVERRIDE_SLIP"},
        "known_conflict_cards": {row["card_no"] for row in conflicts} == {"PROC019", "PROC009", "PROC055", "PROC078"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
