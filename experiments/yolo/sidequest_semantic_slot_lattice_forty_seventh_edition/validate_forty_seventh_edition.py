#!/usr/bin/env python3
"""Consistency checks for the finite compositional slot lattice."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cells = read("FORTY_SEVENTH_144_SLOT_LATTICE.tsv")
    predictions = read("FORTY_SEVENTH_24_EMPTY_CELL_PREDICTIONS.tsv")
    owners = read("FORTY_SEVENTH_120_OWNER_PREDICTIONS.tsv")
    per_prediction = Counter(row["cell_id"] for row in owners)
    checks = {
        "one_hundred_forty_four_cells": len(cells) == 144,
        "twelve_bases": len({row["base"] for row in cells}) == 12,
        "twelve_endings": len({row["ending"] for row in cells}) == 12,
        "cells_unique": len({row["cell_id"] for row in cells}) == 144,
        "sequences_unique": len({row["normalized_atom_sequence"] for row in cells}) == 144,
        "fifty_five_observed": sum(row["status"] == "OBSERVED" for row in cells) == 55,
        "one_hundred_seventy_nine_groups": sum(int(row["observed_group_count"]) for row in cells) == 179,
        "eighty_nine_empty": sum(row["status"] == "EMPTY_WELL_FORMED_PREDICTION" for row in cells) == 89,
        "twenty_four_predictions": len(predictions) == 24,
        "all_predictions_empty": all(row["status"] == "EMPTY_WELL_FORMED_PREDICTION" and int(row["observed_group_count"]) == 0 for row in predictions),
        "ranks_complete": [int(row["prediction_rank"]) for row in predictions] == list(range(1, 25)),
        "one_hundred_twenty_owner_predictions": len(owners) == 120,
        "five_owners_each": all(per_prediction[row["cell_id"]] == 5 for row in predictions),
        "no_surface_invented": all(row["surface_form"] == "NOT_INVENTED" for row in owners),
        "book_exists": (OUT / "FORTY_SEVENTH_SLOT_LATTICE_BOOK.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
