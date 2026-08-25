#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    drawer = read_tsv("PASS994_SECOND_COMPOSITION_DRAWER.tsv")
    grid = read_tsv("PASS994_EIGHT_BY_EIGHT_COMPOSITION_GRID.tsv")
    phrases = read_tsv("PASS994_TWENTY_APPRENTICE_PHRASES.tsv")
    checks = {
        "drawer_70": len(drawer) == 70,
        "drawer_events_287": sum(int(row["events"]) for row in drawer) == 287,
        "cross_page_63": sum(int(row["page_count"]) >= 2 for row in drawer) == 63,
        "all_recurrent": all(int(row["events"]) >= 3 for row in drawer),
        "all_composite": all("+" in row["component_recipe"] for row in drawer),
        "all_concrete": all(row["natural_apprentice_reading_de"].strip() for row in drawer),
        "grid_64": len(grid) == 64,
        "grid_unique": len({(row["left_root"], row["right_root"]) for row in grid}) == 64,
        "phrases_20": len(phrases) == 20,
        "no_new_root_placeholder": all("UNKNOWN" not in str(row) and "EXEMPLAR" not in str(row) for row in drawer),
        "sealed_absent": not any("f84" in str(row).lower() for row in drawer + grid + phrases),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS994_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
