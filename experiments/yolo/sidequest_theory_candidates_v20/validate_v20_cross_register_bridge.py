#!/usr/bin/env python3
"""Validate the bounded V20 bridge-card revision."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    audit = read("V20_CROSS_REGISTER_CARD_AUDIT.tsv")
    occurrences = read("V20_136_OCCURRENCE_LEDGER.tsv")
    lexicon = read("V20_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read("V20_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    assert len(audit) == 17
    assert len(occurrences) == 136
    assert sum(row["disposition"] == "REVISED_CROSS_REGISTER_DEFAULT"
               for row in audit) == 4
    assert {row["register_side"] for row in occurrences} == {"HERBAL", "BIO"}
    assert len(lexicon) == 569
    assert len(ledger) == 776
    assert all(row["default_English"].strip() for row in ledger)
    assert all(0 <= float(row["confidence"]) <= 1 for row in ledger)
    assert not any(row["source_class"].startswith(".") or
                   row["source_class"].replace(".", "", 1).isdigit()
                   for row in ledger)
    assert not any(row["page"].startswith("f84") for row in ledger)
    result = {
        "schema": "SIDEQUEST_V20_CROSS_REGISTER_BRIDGE_VALIDATION_V1",
        "status": "PASS",
        "bridge_cards": 17,
        "bridge_occurrences": 136,
        "preserved_cards": 13,
        "revised_cards": 4,
        "revised_events": 23,
        "complete_lexicon_rows": 569,
        "complete_ledger_rows": 776,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
        "claim_ceiling": "Concrete speculative bridge instructions, not decoded lexemes.",
    }
    (HERE / "V20_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
