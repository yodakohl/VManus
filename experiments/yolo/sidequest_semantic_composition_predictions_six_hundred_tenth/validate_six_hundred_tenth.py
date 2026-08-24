#!/usr/bin/env python3
"""Validate the twelve bounded component predictions."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    predictions = read("SIX_HUNDRED_TENTH_TWELVE_COMPONENT_PREDICTIONS.tsv")
    grids = read("SIX_HUNDRED_TENTH_FIVE_PRODUCTIVE_GRIDS.tsv")
    collisions = [row for row in predictions if row["result"] == "SURFACE_COLLISION_DIFFERENT_PARSE"]
    checks = {
        "predictions12": len(predictions) == 12 and len({row["prediction_id"] for row in predictions}) == 12,
        "all_semantic_combinations_absent": all(row["exact_semantic_card_present"] == "NO" for row in predictions),
        "eleven_surface_absent": sum(row["exact_surface_present"] == "NO" for row in predictions) == 11,
        "one_surface_collision": len(collisions) == 1 and collisions[0]["guessed_surface_family"] == "lchedy",
        "collision_parse_distinct": collisions[0]["predicted_semantic_parse"] != collisions[0]["exact_surface_existing_parse"],
        "all_nearest_supplied": all(row["nearest_surface_1"] and int(row["nearest_distance_1"]) >= 0 for row in predictions),
        "grids5": len(grids) == 5,
        "no_promotions": not any(row["result"] == "ALREADY_PRESENT_SEMANTIC_CARD" for row in predictions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
