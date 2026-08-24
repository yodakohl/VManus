#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cases = read("FOUR_HUNDRED_EIGHTY_SIXTH_113_EXCEPTION_RECLASSIFICATION.tsv")
    rules = read("FOUR_HUNDRED_EIGHTY_SIXTH_FIVE_GENERATIVE_ALLOGRAPH_RULES.tsv")
    manual = read("FOUR_HUNDRED_EIGHTY_SIXTH_169_ITEM_GENERATIVE_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_EIGHTY_SIXTH_776_ADMISSIBLE_SURFACE_LEDGER.tsv")
    classes = Counter(row["generative_class"] for row in cases)
    checks = {
        "cases_113": len(cases) == 113,
        "entry_wrapper_102": classes["ENTRY_WRAPPER_ALLOGRAPH"] == 102,
        "inner_y_8": classes["INNER_Y_ALLOGRAPH"] == 8,
        "inner_aiin_1": classes["INNER_AIIN_ALLOGRAPH"] == 1,
        "inner_al_1": classes["INNER_AL_ALLOGRAPH"] == 1,
        "inner_ar_1": classes["INNER_AR_ALLOGRAPH"] == 1,
        "all_cases_admitted": all(row["observed_admitted"] == "YES" for row in cases),
        "five_rules": len(rules) == 5,
        "manual_169": len(manual) == 169,
        "ledger_776": len(ledger) == 776,
        "deterministic_663": sum(row["exact_surface_choice_deterministic"] == "YES" for row in ledger) == 663,
        "flexible_113": sum(row["exact_surface_choice_deterministic"] == "NO" for row in ledger) == 113,
        "all_observed_admitted": all(row["observed_surface_admitted"] == "YES" for row in ledger),
        "prose_381": sum(row["domain"] == "PROSE" for row in ledger) == 381,
        "astro_395": sum(row["domain"] == "ASTRO" for row in ledger) == 395,
        "fixed_pages_only": {row["page"] for row in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
