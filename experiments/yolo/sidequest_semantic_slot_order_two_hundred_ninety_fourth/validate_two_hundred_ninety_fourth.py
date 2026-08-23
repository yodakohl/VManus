#!/usr/bin/env python3
"""Validate the Pass-294 slot ordering manual."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    cards = read("TWO_HUNDRED_NINETY_FOURTH_64_SLOT_ORDER_CARDS.tsv")
    exceptions = read("TWO_HUNDRED_NINETY_FOURTH_2_FRONTED_EXCEPTIONS.tsv")
    pairs = read("TWO_HUNDRED_NINETY_FOURTH_PAIRWISE_SLOT_ORDER.tsv")
    ol = [row for row in cards if row["ol_placement"] != "NO_OL"]
    checks = {
        "slot_cards_64": len(cards) == 64,
        "slot_events_115": sum(int(row["event_support"]) for row in cards) == 115,
        "default_fit_62": sum(row["fits_default_slot_order"] == "YES" for row in cards) == 62,
        "exceptions_2": len(exceptions) == 2 and {row["canonical_surface"] for row in exceptions} == {"ycheor", "chealror"},
        "ol_mobile_13": len(ol) == 13,
        "ol_postposed_2": sum(row["ol_placement"] == "POSTPOSED_AFTER_CONTENT" for row in ol) == 2,
        "pair_table_nonempty": len(pairs) >= 10,
        "all_component_orders_present": all(row["visible_component_order"] and row["visible_macro_order"] for row in cards),
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_FOURTH_64_SLOT_ORDER_CARDS.tsv", HERE / "TWO_HUNDRED_NINETY_FOURTH_SLOT_ORDER_MANUAL.md", HERE / "TWO_HUNDRED_NINETY_FOURTH_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
