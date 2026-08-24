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
    lookups = read("THREE_HUNDRED_SIXTY_EIGHTH_TEN_SURFACE_LOOKUPS.tsv")
    readings = read("THREE_HUNDRED_SIXTY_EIGHTH_THREE_FREE_READINGS.tsv")
    checks = {
        "ten_lookups": len(lookups) == 10 and [int(r["position"]) for r in lookups] == list(range(1, 11)),
        "all_surfaces_unique": all(r["surface_candidate_cards"] == "1" for r in lookups),
        "no_formulas": all(r["formula_consulted"] == "NO" for r in lookups),
        "no_pages": all(r["running_page_consulted"] == "NO" for r in lookups),
        "two_cycles": {r["inferred_microcycle"] for r in lookups} == {"C1", "C2"},
        "one_slot_drop": sum(r["boundary_before"] == "NEW_MICROCYCLE_BY_SLOT_DROP" for r in lookups) == 1,
        "three_readings": len(readings) == 3 and sum(r["status"] == "SELECTED" for r in readings) == 1,
        "neutral_adds_zero": next(r for r in readings if r["status"] == "SELECTED")["semantic_additions"] == "0",
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
