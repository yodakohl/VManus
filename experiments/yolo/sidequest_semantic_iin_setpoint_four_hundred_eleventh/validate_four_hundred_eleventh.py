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
    bare = read("FOUR_HUNDRED_ELEVENTH_TWO_BARE_IIN_ROUTINES.tsv")
    models = read("FOUR_HUNDRED_ELEVENTH_FOUR_IIN_MODELS.tsv")
    family = read("FOUR_HUNDRED_ELEVENTH_FOUR_IIN_FAMILY_MEMBERS.tsv")
    statements = read("FOUR_HUNDRED_ELEVENTH_TWO_REWRITTEN_STATEMENTS.tsv")
    checks = {
        "two_bare_occurrences": len(bare) == 2,
        "same_exact_tuple": len({row["joint_tuple_id"] for row in bare}) == 1,
        "same_small_value": {row["shared_small_value_de"] for row in bare} == {"Sollstand"},
        "different_records": {row["record"] for row in bare} == {"B1", "B3"},
        "four_models": len(models) == 4,
        "one_selected_model": [row["candidate"] for row in models if row["decision"] == "SELECT"] == ["SOLLSTAND"],
        "four_family_members": len(family) == 4,
        "family_covers_all_hulls": {row["composition"] for row in family} == {"IIN", "K+IIN", "DA+IIN"},
        "two_complete_statements": len(statements) == 2,
        "no_old_generic_gloss": all("Zielstufe" not in value for rows in (bare, family, statements) for row in rows for value in row.values()),
        "no_forbidden_pages": all("f84" not in value.lower() for rows in (bare, models, family, statements) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_ELEVENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
