#!/usr/bin/env python3
"""Validate semantic slot counts around motifs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    contexts = rows("SIX_HUNDRED_FIFTY_FOURTH_25_SLOT_CONTEXTS.tsv")
    aggregate = rows("SIX_HUNDRED_FIFTY_FOURTH_3_SLOT_POLARITIES.tsv")
    closes = rows("SIX_HUNDRED_FIFTY_FOURTH_5_PRECLOSE_CHAINS.tsv")
    counts = {slot: sum(row["slot"] == slot for row in contexts) for slot in ("PRE_BINDER", "POST_BINDER", "PRE_CLOSE")}
    checks = {
        "twenty_five_contexts": len(contexts) == 25,
        "slot_partition": counts == {"PRE_BINDER": 8, "POST_BINDER": 12, "PRE_CLOSE": 5},
        "three_aggregates": len(aggregate) == 3,
        "five_preclose_chains": len(closes) == 5,
        "six_of_eight_prebinder_transitions": sum(row["slot"] == "PRE_BINDER" and row["has_transition_or_operation"] == "YES" for row in contexts) == 6,
        "ten_of_twelve_postbinder_payloads": sum(row["slot"] == "POST_BINDER" and row["has_payload_configuration"] == "YES" for row in contexts) == 10,
        "five_of_five_preclose_anchors": all(row["anchored_in_item_or_amount"] == "YES" for row in closes),
        "all_source_cards_present": all(row["neighbour_card"].startswith("PROC") for row in contexts),
        "no_empty_readings": all(row["neighbour_reading_de"] for row in contexts),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
