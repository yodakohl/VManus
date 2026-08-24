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
    modules = read("SIX_HUNDRED_TWENTY_SECOND_8_MODULE_CONTRAST.tsv")
    components = read("SIX_HUNDRED_TWENTY_SECOND_32_COMPONENT_CONTRAST.tsv")
    cards = read("SIX_HUNDRED_TWENTY_SECOND_94_CARD_CONTRAST.tsv")
    statements = read("SIX_HUNDRED_TWENTY_SECOND_48_STATEMENT_CONTRAST.tsv")
    checks = {
        "modules8": len(modules) == 8 and all(int(row["c1_statements"]) > 0 and int(row["c2_statements"]) > 0 for row in modules),
        "components32": len(components) == 32,
        "shared_components25": sum(row["status"] == "SHARED" for row in components) == 25,
        "c1_only4": sum(row["status"] == "C1_ONLY" for row in components) == 4,
        "c2_only3": sum(row["status"] == "C2_ONLY" for row in components) == 3,
        "cards94": len(cards) == 94,
        "shared_cards17": sum(row["status"] == "SHARED" for row in cards) == 17,
        "statements48": len(statements) == 48 and sum(int(row["event_count"]) for row in statements) == 166,
        "cases_c1_c2": {row["case_id"] for row in statements} == {"C1", "C2"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
