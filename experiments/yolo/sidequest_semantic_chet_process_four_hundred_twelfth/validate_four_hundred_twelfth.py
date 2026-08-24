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
    occ = read("FOUR_HUNDRED_TWELFTH_TWO_CHET_OCCURRENCES.tsv")
    models = read("FOUR_HUNDRED_TWELFTH_FOUR_CHET_MODELS.tsv")
    contrasts = read("FOUR_HUNDRED_TWELFTH_FIVE_OPERATION_CONTRASTS.tsv")
    statements = read("FOUR_HUNDRED_TWELFTH_TWO_REVISED_STATEMENTS.tsv")
    checks = {
        "two_exact_occurrences": len(occ) == 2,
        "one_exact_card": len({row["joint_tuple_id"] for row in occ}) == 1,
        "two_sections": {row["record"] for row in occ} == {"H1", "B3"},
        "portable_value_invariant": {row["portable_value_de"] for row in occ} == {"bearbeiten"},
        "four_models": len(models) == 4,
        "selected_bearbeiten": [row["candidate"] for row in models if row["decision"] == "SELECT"] == ["BEARBEITEN"],
        "five_operation_contrasts": len(contrasts) == 5,
        "two_revised_statements": len(statements) == 2,
        "no_primary_zerkleinern": all("zerkleinern" not in row["revised_card_sequence_de"].lower() for row in statements),
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (occ, models, contrasts, statements) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWELFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
