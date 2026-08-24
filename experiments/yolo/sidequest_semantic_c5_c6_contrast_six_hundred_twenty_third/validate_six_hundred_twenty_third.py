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
    modules = read("SIX_HUNDRED_TWENTY_THIRD_7_MODULE_CONTRAST.tsv")
    components = read("SIX_HUNDRED_TWENTY_THIRD_26_COMPONENT_CONTRAST.tsv")
    cards = read("SIX_HUNDRED_TWENTY_THIRD_35_CARD_CONTRAST.tsv")
    statements = read("SIX_HUNDRED_TWENTY_THIRD_10_STATEMENT_CONTRAST.tsv")
    cases = read("SIX_HUNDRED_TWENTY_THIRD_6_REVISED_CASE_NOUN_LEDGER.tsv")
    c6 = next(row for row in cases if row["case_id"] == "C6")
    checks = {
        "modules7": len(modules) == 7,
        "components26": len(components) == 26,
        "shared_components10": sum(row["status"] == "SHARED" for row in components) == 10,
        "c5_only14": sum(row["status"] == "C5_ONLY" for row in components) == 14,
        "c6_only2": sum(row["status"] == "C6_ONLY" for row in components) == 2,
        "cards35": len(cards) == 35 and sum(row["status"] == "SHARED" for row in cards) == 2,
        "statements10": len(statements) == 10 and sum(int(row["event_count"]) for row in statements) == 47,
        "cases6": len(cases) == 6,
        "c6_revised": c6["c5_link_status"] == "C5_PRODUCT_COMPATIBLE_BUT_NOT_EXPLICITLY_BOUND" and "optional" in c6["application_de"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
