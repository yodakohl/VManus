#!/usr/bin/env python3
"""Validate the fiftieth-edition workshop compiler."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows = read_tsv("FIFTIETH_144_COMPILER_DECISIONS.tsv")
    licensed = read_tsv("FIFTIETH_79_LICENSED_COMMANDS.tsv")
    rejected = read_tsv("FIFTIETH_65_REJECTED_CELLS.tsv")
    counts = Counter(row["compiler_branch"] for row in rows)
    checks = {
        "exactly_144_cells": len(rows) == 144,
        "unique_cells": len({row["cell_id"] for row in rows}) == 144,
        "exactly_79_licensed": len(licensed) == 79,
        "exactly_65_rejected": len(rejected) == 65,
        "observed_branch_55": counts["USE_OBSERVED_FUSED_CARD"] == 55,
        "analytic_branch_7": counts["USE_ANALYTIC_TWO_CARD_FORM"] == 7,
        "paraphrase_branch_17": counts["USE_CONTROLLED_PARAPHRASE"] == 17,
        "reject_branch_65": counts["REJECT_UNLICENSED_EMPTY_CELL"] == 65,
        "licensed_partition_exact": {row["cell_id"] for row in licensed}.isdisjoint({row["cell_id"] for row in rejected}) and len(licensed) + len(rejected) == 144,
        "no_surface_for_rejects": all(row["output_surface_sequence"] == "NONE" for row in rejected),
        "surfaces_for_all_licensed": all(row["output_surface_sequence"] != "NONE" for row in licensed),
        "no_new_fused_claim_for_empty_cells": all(row["exact_registered_fused_form"] != "YES" for row in rows if row["lattice_status"] != "OBSERVED"),
        "fixed_pages_only": all(not any(token in "\t".join(row.values()).lower() for token in ("f84r", "f84v", "f84")) for row in rows),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "counts": dict(counts)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
