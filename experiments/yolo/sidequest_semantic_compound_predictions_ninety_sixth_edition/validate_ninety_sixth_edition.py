#!/usr/bin/env python3
"""Validate the compound prediction inventory."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    predictions = rows("NINETY_SIXTH_36_COMPOUND_PREDICTIONS.tsv")
    matches = rows("NINETY_SIXTH_OBSERVED_COMPOUND_MATCHES.tsv")
    gaps = rows("NINETY_SIXTH_UNFILLED_COMPOUND_CELLS.tsv")
    checks = {
        "predictions_36": len(predictions) == 36,
        "prediction_ids_unique": len({row["prediction_id"] for row in predictions}) == 36,
        "all_meanings_short": all(row["predicted_workshop_meaning_de"] and len(row["predicted_workshop_meaning_de"].split()) <= 9 for row in predictions),
        "matches_consistent": all(int(row["event_count"]) >= 1 and row["observed_surface"] != "NONE" for row in matches),
        "gaps_exact": {row["prediction_id"] for row in gaps} == {row["prediction_id"] for row in predictions if row["matched_surfaces"] == "NONE"},
        "all_statuses_known": set(row["status"] for row in predictions) <= {"UNFILLED_PRODUCTIVE_CELL_ON_FIXED_PAGES", "OBSERVED_COLLISION_SENSITIVE", "OBSERVED_WITH_SURFACE_VARIANTS", "OBSERVED_CLEAN"},
        "composition_rule_fixed": all(row["interpretation_rule"] == "COMPOSE_COMPONENT_VALUES__DO_NOT_ADD_RICH_NOUN" for row in predictions),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in predictions + matches),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "unfilled_count": len(gaps)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
