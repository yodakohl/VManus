#!/usr/bin/env python3
"""Validate Pass 730 source/target/water split."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SEVEN_HUNDRED_THIRTIETH_3_DIRECTION_ROOTS.tsv")
    pairs = read("SEVEN_HUNDRED_THIRTIETH_4_SOURCE_TARGET_PAIRS.tsv")
    dcards = read("SEVEN_HUNDRED_THIRTIETH_37_DIRECTION_CARDS.tsv")
    occurrences = read("SEVEN_HUNDRED_THIRTIETH_58_DIRECTION_OCCURRENCES.tsv")
    cards = read("SEVEN_HUNDRED_THIRTIETH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTIETH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTIETH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTIETH_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    root_counts = {row["root"]: (row["short_value_de"], int(row["exact_cards"]), int(row["events"])) for row in roots}
    checks = {
        "root_counts_exact": root_counts == {"AR": ("QUELLE", 10, 14), "AL": ("ZIELSTELLE", 22, 39), "AIR": ("WASSER", 5, 5)},
        "pairs_four": len(pairs) == 4 and {row["pair_id"] for row in pairs} == {"DIR01", "DIR02", "DIR03", "DIR04"},
        "direction_cards_37": len(dcards) == 37 and len({row["exact_card_id"] for row in dcards}) == 37,
        "occurrences_58": len(occurrences) == 58 and len({row["event_id"] for row in occurrences}) == 58,
        "complete_173_381_116_11": len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(records) == 11,
        "event_card_readings_match": all(next(card["pass730_reading_de"] for card in cards if card["exact_card_id"] == row["card_no"]) == row["pass730_semantic_de"] for row in events),
        "all_ar_source": all("QUELLE" in row["pass730_atomic_reading_de"] for row in occurrences if row["root"] == "AR"),
        "all_al_target_site": all("ZIELSTELLE" in row["pass730_atomic_reading_de"] for row in occurrences if row["root"] == "AL"),
        "all_air_water": all("WASSER" in row["pass730_atomic_reading_de"] for row in occurrences if row["root"] == "AIR"),
        "air_not_split": next(row for row in roots if row["root"] == "AIR")["nesting_rule"] == "ATOMIC_ROOT__DO_NOT_SPLIT",
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTIETH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
