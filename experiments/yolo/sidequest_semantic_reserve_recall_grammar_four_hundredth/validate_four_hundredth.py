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
    branch = read("FOUR_HUNDREDTH_FOUR_H3_BRANCH_CARDS.tsv")
    siblings = read("FOUR_HUNDREDTH_H1_H2_H5_SIBLINGS.tsv")
    families = read("FOUR_HUNDREDTH_FUNCTIONAL_FAMILIES.tsv")
    checks = {
        "four_branch_cards": len(branch) == 4,
        "branch_events_exact": {row["event_id"] for row in branch} == {"E046", "E047", "E052", "E053"},
        "two_local_whole_cards": sum(row["portability"] == "H3_WHOLE_CARD" for row in branch) == 2,
        "two_compositional_cards": sum(row["decision"] == "READ_COMPOSITIONALLY" for row in branch) == 2,
        "nine_siblings": len(siblings) == 9,
        "siblings_only_h1_h2_h5": {row["record"] for row in siblings} == {"H1", "H2", "H5"},
        "eight_family_rows": len(families) == 8,
        "ol_count_nineteen": any(row["family"] == "OL" and row["visible_events"] == "19" for row in families),
        "no_fake_second_reserve_pair": not any(row["function"] in {"RESERVE", "RECALL"} for row in siblings),
        "all_concrete": all(row["working_reading_de"] for row in branch + siblings),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDREDTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
