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
    occ = read("FOUR_HUNDRED_EIGHTEENTH_SIXTEEN_AIN_OCCURRENCES.tsv")
    family = read("FOUR_HUNDRED_EIGHTEENTH_SEVEN_AIN_CARDS.tsv")
    models = read("FOUR_HUNDRED_EIGHTEENTH_FOUR_AIN_MODELS.tsv")
    b2 = read("FOUR_HUNDRED_EIGHTEENTH_B2_DOUBLE_PORTION.tsv")
    contrast = read("FOUR_HUNDRED_EIGHTEENTH_AIN_AIIN_IIN_CONTRAST.tsv")
    checks = {
        "sixteen_ain_events": len(occ) == 16,
        "seven_ain_cards": len(family) == 7,
        "ain_invariant": {row["ain_invariant_de"] for row in occ} == {"Portion"},
        "family_event_sum": sum(int(row["events"]) for row in family) == 16,
        "four_models": len(models) == 4,
        "portion_selected": [row["candidate"] for row in models if row["decision"] == "SELECT"] == ["PORTION"],
        "four_b2_events": len(b2) == 4,
        "two_additions": [row["operation_instance"] for row in b2].count("ADD_1") == 1 and [row["operation_instance"] for row in b2].count("ADD_2") == 1,
        "same_source_second_addition": b2[2]["source_scope"] == "SAME_SOURCE",
        "three_quantity_families": len(contrast) == 3,
        "quantity_values_distinct": len({row["small_value_de"] for row in contrast}) == 3,
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (occ, family, models, b2, contrast) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
