#!/usr/bin/env python3
"""Consistency checks for constrained surface realization."""

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
    decisions = read("FORTY_EIGHTH_24_SURFACE_DECISIONS.tsv")
    copies = read("FORTY_EIGHTH_28_ANALYTIC_COPIES.tsv")
    blocked = read("FORTY_EIGHTH_17_BLOCKED_COMPOUNDS.tsv")
    per_cell = Counter(row["cell_id"] for row in copies)
    checks = {
        "twenty_four_decisions": len(decisions) == 24,
        "ranks_complete": [int(row["prediction_rank"]) for row in decisions] == list(range(1, 25)),
        "no_fused_surface_claimed": all(row["exact_fused_surface_available"] == "NO" for row in decisions),
        "seven_analytic": sum(row["analytic_two_card_expression_available"] == "YES" for row in decisions) == 7,
        "twenty_eight_copies": len(copies) == 28,
        "four_copies_per_analytic_cell": all(per_cell[row["cell_id"]] == 4 for row in decisions if row["analytic_two_card_expression_available"] == "YES"),
        "all_copies_observed_surfaces": all(row["uses_only_observed_surfaces"] == "YES" and row["new_surface_invented"] == "NO" for row in copies),
        "boundary_change_explicit": all(row["word_boundary_changed"].startswith("YES_") for row in copies),
        "seventeen_blocked": len(blocked) == 17,
        "all_blocked_missing_inventory": all(row["missing_inventory"] != "NONE" for row in blocked),
        "book_exists": (OUT / "FORTY_EIGHTH_SURFACE_REALIZATION_BOOK.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
