#!/usr/bin/env python3
"""Validate Pass 713 boundary-carrier rule."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("SEVEN_HUNDRED_THIRTEENTH_35_BOUNDARY_CARRIER_EVENTS.tsv")
    families = read("SEVEN_HUNDRED_THIRTEENTH_4_FAMILY_RULES.tsv")
    models = read("SEVEN_HUNDRED_THIRTEENTH_6_MODEL_COMPARISON.tsv")
    overrides = read("SEVEN_HUNDRED_THIRTEENTH_5_OVERRIDE_SLIPS.tsv")
    chosen = next(row for row in models if row["model"] == "LOCUS_FIRST_MARKED")
    checks = {
        "events_35": len(events) == 35,
        "families_4": len(families) == 4,
        "recipes_exact": {row["component_recipe"] for row in families} == {"OK+Y", "CHD+Y", "CHD+DY", "OK+CHD+DY"},
        "marked_10": sum(row["observed_variant"] == "MARKED_CARRIER" for row in events) == 10,
        "plain_25": sum(row["observed_variant"] == "PLAIN" for row in events) == 25,
        "first_6_marked_1_plain": sum(row["locus_position"] == "FIRST" and row["observed_variant"] == "MARKED_CARRIER" for row in events) == 6 and sum(row["locus_position"] == "FIRST" and row["observed_variant"] == "PLAIN" for row in events) == 1,
        "nonfirst_4_marked_24_plain": sum(row["locus_position"] != "FIRST" and row["observed_variant"] == "MARKED_CARRIER" for row in events) == 4 and sum(row["locus_position"] != "FIRST" and row["observed_variant"] == "PLAIN" for row in events) == 24,
        "chosen_30_of_35": chosen["correct"] == "30" and chosen["errors"] == "5",
        "overrides_5": len(overrides) == 5,
        "all_overrides_are_errors": {row["event_id"] for row in overrides} == {row["event_id"] for row in events if row["boundary_prior_correct"] == "NO"},
        "no_semantic_splits": all(row["semantic_decision"] == "ONE_RECIPE__NO_MEANING_SPLIT" for row in families),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTEENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
