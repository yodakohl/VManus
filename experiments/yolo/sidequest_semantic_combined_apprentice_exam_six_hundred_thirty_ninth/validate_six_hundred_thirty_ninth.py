#!/usr/bin/env python3
"""Validate the combined prose/Astro apprentice examination."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    prose = read("SIX_HUNDRED_THIRTY_NINTH_6_STEP_C3_EXAM.tsv")
    correction = read("SIX_HUNDRED_THIRTY_NINTH_3_STAGE_PROSE_CORRECTION.tsv")
    astro = read("SIX_HUNDRED_THIRTY_NINTH_6_ROW_ASTRO_COPY_CORRECTION.tsv")
    checks = {
        "six_prose_steps": len(prose) == 6 and [row["step"] for row in prose] == [str(i) for i in range(1, 7)],
        "expected_c3_sequence": " ".join(row["surface"] for row in prose) == "qokaiin qokal cfhy cphy tshey shedy",
        "all_existing_inventory": all(row["existing_inventory"] == "YES" for row in prose),
        "three_correction_stages": [row["stage"] for row in correction] == ["INTENDED_JOB", "APPRENTICE_ERROR", "MASTER_CORRECTION"],
        "error_keeps_case": correction[1]["case_selected"] == "C3",
        "error_reverses_process": correction[1]["wring_before_fill"] == "NO" and correction[2]["wring_before_fill"] == "YES",
        "six_astro_rows": len(astro) == 6,
        "astro_two_groups_each": all(sum(row["stage"] == stage for row in astro) == 2 for stage in {"MASTER_MODEL", "APPRENTICE_ERROR", "MASTER_CORRECTION"}),
        "astro_error_both_positions": sum(row["stage"] == "APPRENTICE_ERROR" and row["matches_master_position"] == "NO" for row in astro) == 2,
        "astro_correction_both_positions": sum(row["stage"] == "MASTER_CORRECTION" and row["matches_master_position"] == "YES" for row in astro) == 2,
        "fixed_page_locus": all(row["page"] == "f69v" and row["locus"] == "f69v.31" for row in astro),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
