#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    candidates = rows("HUNDRED_SEVENTY_FIRST_4_PRODUCT_CLASSES.tsv")
    clues = rows("HUNDRED_SEVENTY_FIRST_5_PRODUCT_CLUES.tsv")
    events = rows("HUNDRED_SEVENTY_FIRST_18_EVENT_F55V_STOCK_READING.tsv")
    sources = rows("HUNDRED_SEVENTY_FIRST_HISTORICAL_COMPARATORS.tsv")
    checks = {
        "four_classes": len(candidates) == 4,
        "one_selection": sum(row["selection"] == "SELECTED" for row in candidates) == 1,
        "selection_has_top_score": next(int(row["total_0_10"]) for row in candidates if row["selection"] == "SELECTED") == max(int(row["total_0_10"]) for row in candidates),
        "five_clues": len(clues) == 5,
        "all_18_events": [int(row["event_serial"]) for row in events] == list(range(56, 74)),
        "all_f55v": {row["page"] for row in events} == {"f55v"},
        "same_product_class": {row["selected_product_class"] for row in events} == {"STORED_TWO_PART_PLANT_STOCK"},
        "no_dictionary_change": {row["dictionary_change"] for row in events} == {"NO"},
        "all_concrete": all(row["product_expansion_de"].strip() for row in events),
        "three_comparators": len(sources) == 3,
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
