#!/usr/bin/env python3
"""Validate Pass 710 all-statement dockets."""

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
    components = read("SEVEN_HUNDRED_TENTH_39_COMPONENT_DOCKET_MAP.tsv")
    dockets = read("SEVEN_HUNDRED_TENTH_116_SHORTEST_DOCKETS.tsv")
    rebuilds = read("SEVEN_HUNDRED_TENTH_381_CARD_REBUILDS.tsv")
    ambiguity = read("SEVEN_HUNDRED_TENTH_DOCKET_AMBIGUITY.tsv")
    records = read("SEVEN_HUNDRED_TENTH_11_RECORD_DOCKET_ROLLS.tsv")
    slots = Counter(int(row["nonempty_slots"]) for row in dockets)
    checks = {
        "components_39": len(components) == 39,
        "components_unique": len({row["component"] for row in components}) == 39,
        "statements_116": len(dockets) == 116,
        "events_381": len(rebuilds) == 381,
        "records_11": len(records) == 11,
        "raw_tokens_850": sum(int(row["raw_component_tokens"]) for row in dockets) == 850,
        "docket_tokens_666": sum(int(row["deduplicated_docket_components"]) for row in dockets) == 666,
        "nonempty_cells_423": sum(int(row["nonempty_slots"]) for row in dockets) == 423,
        "slot_distribution": slots == {1: 1, 2: 20, 3: 37, 4: 30, 5: 17, 6: 11},
        "all_card_rebuilds_exact": all(row["exact_card_rebuild"] == "YES" for row in rebuilds),
        "one_ambiguous_signature": len(ambiguity) == 1,
        "two_ambiguous_statements": ambiguity[0]["statement_count"] == "2",
        "ninety_six_signatures": len({row["docket_signature"] for row in dockets}) == 96,
        "ninety_five_unique_signatures": len({row["docket_signature"] for row in dockets if row["docket_unique_in_fixed_registry"] == "YES"}) == 95,
        "all_master_addressed": all(row["master_card_address_required"] == "YES" for row in dockets),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
