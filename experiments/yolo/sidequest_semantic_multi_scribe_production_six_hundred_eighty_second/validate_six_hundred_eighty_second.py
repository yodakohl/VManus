#!/usr/bin/env python3
"""Validate the multi-scribe recurrent-recipe traces."""

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
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_second.py")], check=True)
    families = read("SIX_HUNDRED_EIGHTY_SECOND_50_RECURRENT_RECIPE_FAMILIES.tsv")
    traces = read("SIX_HUNDRED_EIGHTY_SECOND_268_MULTI_SCRIBE_TRACES.tsv")
    lessons = read("SIX_HUNDRED_EIGHTY_SECOND_12_TEACHING_FAMILIES.tsv")
    layers = read("SIX_HUNDRED_EIGHTY_SECOND_4_PRODUCTION_LAYERS.tsv")
    checks = {
        "fifty_recurrent_families": len(families) == 50 and all(int(row["events"]) >= 2 for row in families),
        "two_hundred_sixty_eight_traces": len(traces) == 268 and len({row["event_id"] for row in traces}) == 268,
        "family_event_sum": sum(int(row["events"]) for row in families) == 268,
        "forty_five_cross_record": sum(int(row["distinct_records"]) >= 2 for row in families) == 45,
        "forty_one_cross_page": sum(int(row["distinct_pages"]) >= 2 for row in families) == 41,
        "forty_one_card_families": sum(int(row["exact_cards"]) == 1 for row in families) == 40,
        "ten_two_card_families": sum(int(row["exact_cards"]) == 2 for row in families) == 10,
        "fourteen_surface_stable": sum(int(row["surface_forms"]) == 1 for row in families) == 14,
        "thirty_six_surface_variable": sum(int(row["surface_forms"]) > 1 for row in families) == 36,
        "twelve_teaching_families": len(lessons) == 12,
        "four_layers": len(layers) == 4,
        "fixed_pages_only": {row["page"] for row in traces} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
