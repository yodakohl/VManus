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
    modules = read("SIX_HUNDRED_TWENTY_FIRST_8_MODULE_CONTRAST.tsv")
    components = read("SIX_HUNDRED_TWENTY_FIRST_34_COMPONENT_CONTRAST.tsv")
    cards = read("SIX_HUNDRED_TWENTY_FIRST_90_CARD_CONTRAST.tsv")
    statements = read("SIX_HUNDRED_TWENTY_FIRST_58_STATEMENT_CONTRAST.tsv")
    checks = {
        "modules8": len(modules) == 8,
        "components34": len(components) == 34,
        "shared_components23": sum(row["status"] == "SHARED" for row in components) == 23,
        "c3_only7": sum(row["status"] == "C3_ONLY" for row in components) == 7,
        "c4_only4": sum(row["status"] == "C4_ONLY" for row in components) == 4,
        "cards90": len(cards) == 90,
        "shared_cards18": sum(row["status"] == "SHARED" for row in cards) == 18,
        "statements58": len(statements) == 58 and sum(int(row["event_count"]) for row in statements) == 168,
        "cases_c3_c4": {row["case_id"] for row in statements} == {"C3", "C4"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
