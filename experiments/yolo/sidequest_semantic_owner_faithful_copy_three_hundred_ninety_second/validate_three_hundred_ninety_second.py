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
    cards = read("THREE_HUNDRED_NINETY_SECOND_25_OWNER_NATIVE_CARDS.tsv")
    lines = read("THREE_HUNDRED_NINETY_SECOND_SIX_REFLOWED_LINES.tsv")
    reconstructed = read("THREE_HUNDRED_NINETY_SECOND_25_RECONSTRUCTED_CARDS.tsv")
    readings = read("THREE_HUNDRED_NINETY_SECOND_FIVE_GENUINE_READINGS.tsv")
    checks = {
        "twenty_five_cards": len(cards) == 25,
        "owner_split": Counter(row["owner_code"] for row in cards) == {"H4": 18, "B3": 7},
        "all_owner_native": all(row["owner_native"] == "YES" for row in cards),
        "all_registered": all(row["copy_surface"] in row["registered_palette"].split("|") for row in cards),
        "no_values_spoken": all(row["german_value_spoken_to_scribe"] == "NO" for row in cards),
        "six_lines": len(lines) == 6,
        "line_card_sum": sum(int(row["source_cards"]) for row in lines) == 25,
        "one_owner_handoff": sum(row["owner_handoff_before"] == "YES" for row in lines) == 1,
        "one_line_continuation": sum(row["statement_continues_next_line"] == "YES" for row in lines) == 1,
        "five_statements": len(readings) == 5,
        "identity_recovery": len(reconstructed) == 25 and all(row["identity_match"] == "YES" for row in reconstructed),
        "statement_recovery": all(row["copy_preserves_statement"] == "YES" for row in readings),
        "renderer_changed_nonzero": any(row["renderer_changed"] == "YES" for row in cards),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETY_SECOND_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
