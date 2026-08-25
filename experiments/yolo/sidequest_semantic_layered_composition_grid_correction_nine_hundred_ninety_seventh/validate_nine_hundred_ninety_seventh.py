#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    grid = rows("PASS997_CORRECTED_LAYERED_EIGHT_BY_EIGHT_GRID.tsv")
    empty = rows("PASS997_TWENTY_FIVE_TRUE_EMPTY_CELLS.tsv")
    collisions = rows("PASS997_THREE_SURFACE_COLLISIONS.tsv")
    counts = Counter(row["status"] for row in grid)
    checks = {
        "grid_64": len(grid) == 64,
        "grid_unique": len({row["component_recipe"] for row in grid}) == 64,
        "productive_24": counts["BELEGT_PRODUKTIV"] == 24,
        "formula_12": counts["BELEGT_ALS_GELERNTE_FORMEL"] == 12,
        "specialist_1": counts["NUR_GELERNTE_FACHKARTE"] == 1,
        "local_2": counts["NUR_LOKALE_ADRESSE"] == 2,
        "empty_25": counts["NICHT_BELEGT"] == 25 and len(empty) == 25,
        "collisions_3": len(collisions) == 3,
        "collision_recipes": {row["component_recipe"] for row in collisions} == {"S+Y", "CH+Y", "CH+AR"},
        "ok_y_formula": next(row for row in grid if row["component_recipe"] == "OK+Y")["formula_card_events"] == "37",
        "all_empty_concrete": all(row["natural_available_reading_de"].strip() for row in empty),
        "sealed_absent": not any("f84" in str(row).lower() for row in grid + empty + collisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS997_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
