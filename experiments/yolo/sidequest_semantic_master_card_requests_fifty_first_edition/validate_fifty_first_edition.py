#!/usr/bin/env python3
"""Validate the master-card request ranking."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    requests = rows("FIFTY_FIRST_8_MASTER_CARD_REQUESTS.tsv")
    triage = rows("FIFTY_FIRST_65_REJECTION_TRIAGE.tsv")
    approvals = rows("FIFTY_FIRST_25_MEANING_APPROVALS.tsv")
    paired = rows("FIFTY_FIRST_8_DOUBLE_MISSING_CELLS.tsv")
    checks = {
        "eight_missing_card_categories": len(requests) == 8,
        "unique_missing_atoms": len({row["candidate_atom"] for row in requests}) == 8,
        "priority_is_one_to_eight": [int(row["priority_rank"]) for row in requests] == list(range(1, 9)),
        "sixty_five_rejections_triaged": len(triage) == 65,
        "twenty_five_meaning_only": len(approvals) == 25,
        "thirty_two_single_missing": sum(row["triage_category"] == "ONE_MASTER_CARD_MISSING" for row in triage) == 32,
        "eight_double_missing": len(paired) == 8,
        "partition_is_65": len(approvals) + 32 + len(paired) == 65,
        "single_unlock_sum_is_32": sum(int(row["new_commands_unlocked_by_this_card_alone"]) for row in requests) == 32,
        "no_surface_proposed": all(row["surface_proposed"] == "NONE" for row in requests),
        "all_triage_cells_unique": len({row["cell_id"] for row in triage}) == 65,
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in triage),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
