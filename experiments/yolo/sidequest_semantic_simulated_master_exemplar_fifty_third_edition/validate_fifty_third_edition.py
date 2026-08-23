#!/usr/bin/env python3
"""Validate the simulated exemplar without mistaking catalog labels for Voynich forms."""

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
    cards = rows("FIFTY_THIRD_4_MASTER_CATALOG_CARDS.tsv")
    licensed = rows("FIFTY_THIRD_128_LICENSED_EXEMPLAR.tsv")
    requests = rows("FIFTY_THIRD_16_MASTER_REQUEST_SLIPS.tsv")
    traces = rows("FIFTY_THIRD_12_APPRENTICE_TRACES.tsv")
    branches = Counter(row["compiler_branch"] for row in licensed)
    checks = {
        "four_neutral_cards": len(cards) == 4 and {row["catalog_id"] for row in cards} == {"M01", "M02", "M03", "M04"},
        "surfaces_unassigned": all(row["voynich_surface"] == "UNASSIGNED" for row in cards),
        "one_hundred_twenty_eight_commands": len(licensed) == 128 and len({row["cell_id"] for row in licensed}) == 128,
        "sixteen_requests": len(requests) == 16 and len({row["cell_id"] for row in requests}) == 16,
        "complete_144_partition": {row["cell_id"] for row in licensed}.isdisjoint({row["cell_id"] for row in requests}) and len(licensed) + len(requests) == 144,
        "twelve_traces": len(traces) == 12 and Counter(row["lesson_branch"] for row in traces) == Counter({"OBSERVED_FUSED": 3, "ANALYTIC_OBSERVED": 3, "ANALYTIC_MASTER": 3, "CONTROLLED_PARAPHRASE": 3}),
        "licensed_branch_counts": branches == Counter({"ANALYTIC_TWO_CARD_FORM": 61, "OBSERVED_FUSED_CARD": 55, "CONTROLLED_PARAPHRASE": 12}),
        "only_four_remaining_categories": {part for row in requests for part in row["missing_catalog_categories"].split("|")} == {"CLOSE", "E+Y", "SHED", "SOLK"},
        "all_surface_claims_no": all(row["voynich_surface_invented"] == "NO" for row in licensed),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in licensed + requests),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
