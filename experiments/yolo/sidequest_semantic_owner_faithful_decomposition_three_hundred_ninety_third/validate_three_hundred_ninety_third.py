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
    cards = read("THREE_HUNDRED_NINETY_THIRD_25_COMPONENT_NOMENCLATOR_READINGS.tsv")
    statements = read("THREE_HUNDRED_NINETY_THIRD_FIVE_COMPLETE_STATEMENTS.tsv")
    comparison = read("THREE_HUNDRED_NINETY_THIRD_COVERAGE_COMPARISON.tsv")
    checks = {
        "twenty_five_cards": len(cards) == 25,
        "twenty_components": Counter(row["read_route"] for row in cards)["COMPONENT_DIRECT"] == 20,
        "five_wholes": Counter(row["read_route"] for row in cards)["NOMENCLATOR_WHOLE"] == 5,
        "five_statements": len(statements) == 5,
        "statement_card_sum": sum(int(row["card_count"]) for row in statements) == 25,
        "statement_component_sum": sum(int(row["component_cards"]) for row in statements) == 20,
        "statement_whole_sum": sum(int(row["nomenclator_cards"]) for row in statements) == 5,
        "two_comparison_rows": len(comparison) == 2,
        "genuine_eighty_percent": next(row for row in comparison if row["page_model"] == "OWNER_FAITHFUL_H4_B3_COPY")["component_percent"] == "80.0",
        "identities_preserved": all(row["exact_identity_preserved"] == "YES" for row in cards),
        "all_atomic_readings": all(row["short_atomic_reading_de"] for row in cards),
        "all_fluent_statements": all(row["fluent_owner_expansion_de"] for row in statements),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETY_THIRD_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
