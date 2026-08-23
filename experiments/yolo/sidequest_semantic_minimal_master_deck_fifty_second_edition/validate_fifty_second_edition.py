#!/usr/bin/env python3
"""Validate exhaustive missing-card subset enumeration and the four-card choice."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subsets = rows("FIFTY_SECOND_256_SUBSET_RESULTS.tsv")
    frontier = rows("FIFTY_SECOND_9_BUDGET_FRONTIER.tsv")
    compiler = rows("FIFTY_SECOND_144_FOUR_CARD_COMPILER.tsv")
    branches = Counter(row["four_card_branch"] for row in compiler)
    chosen = next(row for row in subsets if row["selected_cards"] == "CHK|CKHE|E+CLOSE|EE+CLOSE")
    checks = {
        "all_256_subsets": len(subsets) == 256 and len({row["subset_id"] for row in subsets}) == 256,
        "nine_budgets": len(frontier) == 9 and [int(row["card_budget"]) for row in frontier] == list(range(9)),
        "frontier_monotone": all(int(frontier[index]["total_licensed_commands"]) <= int(frontier[index + 1]["total_licensed_commands"]) for index in range(8)),
        "recommended_four_cards": chosen["card_count"] == "4",
        "recommended_128_licensed": chosen["total_licensed_commands"] == "128",
        "recommended_16_rejected": chosen["rejected_commands"] == "16",
        "recommended_116_observed_or_analytic": chosen["observed_or_analytic_cells"] == "116",
        "recommended_12_paraphrases": chosen["remaining_controlled_paraphrases"] == "12",
        "compiler_has_144_cells": len(compiler) == 144 and len({row["cell_id"] for row in compiler}) == 144,
        "compiler_branch_total": sum(branches.values()) == 144,
        "compiler_has_16_rejects": branches["REJECT_AND_ASK_MASTER"] == 16,
        "no_new_surface_claim": all(row["new_surface_claimed"] == "NO" for row in compiler),
        "placeholders_explicit": all("<" not in row["output_surface_or_placeholder"] or row["surface_status"] == "HYPOTHETICAL_MASTER_CATEGORY" for row in compiler),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in compiler),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "four_card_branches": dict(branches)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
