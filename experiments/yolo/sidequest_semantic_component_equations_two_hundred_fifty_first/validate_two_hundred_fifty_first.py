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
    dictionary = rows("TWO_HUNDRED_FIFTY_FIRST_REVISED_173_CARD_DICTIONARY.tsv")
    equations = rows("TWO_HUNDRED_FIFTY_FIRST_COMPONENT_EQUATIONS.tsv")
    repairs = rows("TWO_HUNDRED_FIFTY_FIRST_TWO_COLLISION_REPAIRS.tsv")
    triplet = rows("TWO_HUNDRED_FIFTY_FIRST_PORTION_TRIPLET.tsv")
    by_id = {r["master_card_id"]: r for r in dictionary}
    checks = {
        "173_cards": len(dictionary) == 173,
        "173_unique_ids": len(by_id) == 173,
        "two_repairs": len(repairs) == 2,
        "three_portion_cards": len(triplet) == 3,
        "portion_formulas_distinct": len({r["component_formula"] for r in triplet}) == 3,
        "otol_unified": by_id["MC053"]["portable_core_de"] == by_id["MC163"]["portable_core_de"] == "DANACH_WEITER",
        "ykan_is_an": by_id["MC148"]["component_parse"] == "Y + K + AN",
        "no_concrete_conflicts": all(r["equation_status"] != "CONFLICT" for r in equations),
        "common_formulas_restored": all(r["component_parse"] != "COMMON_CORE" for r in dictionary),
        "all_cores_concrete": all(r["portable_core_de"].strip() for r in dictionary),
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in dictionary),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
