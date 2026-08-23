#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    occurrences = rows("TWO_HUNDRED_FIFTY_THIRD_13_ASTRO_OCCURRENCES.tsv")
    comparison = rows("TWO_HUNDRED_FIFTY_THIRD_PROSE_ASTRO_QUANTITY_COMPARISON.tsv")
    counts = Counter(r["quantity_ending"] for r in occurrences)
    checks = {
        "13_occurrences": len(occurrences) == 13,
        "ending_split_11_1_1": counts == {"AIIN": 11, "AIN": 1, "FALSE_FRIEND": 1},
        "four_comparison_rows": len(comparison) == 4,
        "an_absent": all(r["quantity_ending"] != "AN" for r in occurrences),
        "dain_false_friend": {r["master_card_id"] for r in occurrences if r["quantity_ending"] == "FALSE_FRIEND"} == {"MC059"},
        "aiin_pages": {r["page"] for r in occurrences if r["quantity_ending"] == "AIIN"} == {"f67r2", "f69v"},
        "all_readings_concrete": all(r["diagram_local_reading_de"].strip() for r in occurrences),
        "astro_pages_only": {r["page"] for r in occurrences} <= {"f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in occurrences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
