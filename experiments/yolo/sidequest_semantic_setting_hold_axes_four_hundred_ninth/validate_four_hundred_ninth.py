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
    statements = read("FOUR_HUNDRED_NINTH_FOUR_IIN_STATEMENTS.tsv")
    axes = read("FOUR_HUNDRED_NINTH_SIX_AXIS_RULES.tsv")
    pairings = read("FOUR_HUNDRED_NINTH_FOUR_SETTING_HOLD_PAIRINGS.tsv")
    checks = {
        "four_iin_statements": len(statements) == 4,
        "records_exact": {row["record"] for row in statements} == {"H2", "B1", "B3", "B5"},
        "two_explicit_grades": sum(row["hold_event"] != "NONE" for row in statements) == 2,
        "two_unspecified_grades": sum(row["hold_event"] == "NONE" for row in statements) == 2,
        "b1_grade_two": next(row for row in statements if row["record"] == "B1")["hold_surface"] == "olkeedy",
        "b3_grade_one": next(row for row in statements if row["record"] == "B3")["hold_surface"] == "shedy",
        "six_axes": len(axes) == 6,
        "setting_separate": next(row for row in axes if row["axis"] == "SETTING")["scope"] == "target condition",
        "four_pairings": len(pairings) == 4,
        "no_superword_claim": all("..." in row["example"] or row["hold"] == "UNSPECIFIED" for row in pairings),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_NINTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
