#!/usr/bin/env python3
"""Validate Pass 295 transfer-core analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    cards = read("TWO_HUNDRED_NINETY_FIFTH_20_TRANSFER_CORE_CARDS.tsv")
    rules = read("TWO_HUNDRED_NINETY_FIFTH_CHD_CHED_DECISION_TREE.tsv")
    prediction = read("TWO_HUNDRED_NINETY_FIFTH_PCHEDAIN_DERIVATION.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text())
    checks = {
        "twenty_cards": len(cards) == 20,
        "forty_three_events": sum(int(row["event_support"]) for row in cards) == 43,
        "short_eighteen_events": summary["short_or_flexible_events"] == 18,
        "expanded_twenty_five_events": summary["expanded_events"] == 25,
        "all_have_core": all("TRANSFER" in row["transfer_core_atom"] or row["transfer_core_atom"].startswith(("CHD", "CHED")) for row in cards),
        "all_have_sides": all(row["left_of_transfer_core"] and row["right_of_transfer_core"] for row in cards),
        "seven_rules": len(rules) == 7,
        "pchedain_four_steps": len(prediction) == 4 and prediction[-1]["surface"] == "pchedain",
        "pchedain_currently_new": summary["pchedain_visible_now"] is False,
        "current_item_not_always_close": any(row["canonical_surface"] == "chdy" and row["endpoint_interpretation"] == "CURRENT_ITEM_NOT_COMMIT" for row in cards),
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_FIFTH_20_TRANSFER_CORE_CARDS.tsv", HERE / "TWO_HUNDRED_NINETY_FIFTH_TRANSFER_CORE_MANUAL.md", HERE / "TWO_HUNDRED_NINETY_FIFTH_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
