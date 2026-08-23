#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows = read("TWO_HUNDRED_SEVENTY_SEVENTH_40_COMPONENT_REACH.tsv")
    classes = read("TWO_HUNDRED_SEVENTY_SEVENTH_SIX_REACH_CLASSES.tsv")
    expected = {"HERBAL_BIO_ASTRO_CORE": 16, "HERBAL_ASTRO_BRIDGE": 4, "BIO_ASTRO_BRIDGE": 4, "HERBAL_BIO_PROSE_CORE": 2, "HERBAL_SPECIALIST": 7, "BIO_SPECIALIST": 7}
    checks = {
        "40_components": len(rows) == 40,
        "orders_1_40": [int(r["deck_order"]) for r in rows] == list(range(1, 41)),
        "six_classes": len(classes) == 6,
        "reach_counts": Counter(r["reach_class"] for r in rows) == expected,
        "class_sum_40": sum(int(r["component_count"]) for r in classes) == 40,
        "universal_16": sum(r["teaching_status"] == "COMMON_CORE" for r in rows) == 16,
        "seven_each_specialists": sum(r["reach_class"] == "HERBAL_SPECIALIST" for r in rows) == 7 and sum(r["reach_class"] == "BIO_SPECIALIST" for r in rows) == 7,
        "no_unmapped": all(r["reach_class"] not in {"UNMAPPED", "ASTRO_SPECIALIST"} for r in rows),
        "all_values_nonempty": all(r["short_value_de"].strip() for r in rows),
        "all_have_support": all(int(r["herbal_events"]) + int(r["bio_events"]) + int(r["astro_groups"]) > 0 for r in rows),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
