#!/usr/bin/env python3
"""Validate V17 candidate coverage and selected complete propagation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EVASIVE = {"", "unknown", "opaque", "untranslated", "content", "payload",
           "item", "value", "state", "unassigned"}
CONFIG = {
    1: ("exact_tuple_id", "selected_default"),
    2: ("exact_tuple_id", "selected_meaning"),
    3: ("exact_tuple_id", "selected_default"),
    4: ("tuple_id", "selected_default"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []
    expected_ids: set[str] | None = None
    for number, (id_column, selected_column) in CONFIG.items():
        decisions = read(HERE / f"V17_R{number}_RECURRENT_CARD_DECISIONS.tsv")
        occurrences = read(HERE / f"V17_R{number}_ALL_OCCURRENCE_READINGS.tsv")
        assert len(decisions) == 30
        assert len(occurrences) == 217
        ids = {row[id_column] for row in decisions}
        assert len(ids) == 30
        if expected_ids is None:
            expected_ids = ids
        assert ids == expected_ids
        assert all(row[selected_column].strip().lower() not in EVASIVE for row in decisions)
        assert not any(any(value.lower().startswith("f84") for value in row.values())
                       for row in occurrences)
        checks.append({"candidate": f"R{number}", "cards": 30,
                       "occurrences": 217, "concrete_selected_meanings": 30,
                       "f84_rows": 0})

    selected = read(HERE / "V17_SELECTED_RECURRENT_DECK.tsv")
    lexicon = read(HERE / "V17_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read(HERE / "V17_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    assert len(selected) == 30
    assert {row["exact_tuple_id"] for row in selected} == expected_ids
    assert len(lexicon) == 569
    assert len(ledger) == 776
    assert sum(row["exact_tuple_id"] in expected_ids for row in ledger) == 217
    assert all(row["default_English"].strip().lower() not in EVASIVE for row in ledger)
    assert not any(row["page"].lower().startswith("f84") for row in ledger)

    result = {
        "schema": "SIDEQUEST_V17_RECURRENT_DECK_VALIDATION_V1",
        "status": "PASS",
        "candidate_checks": checks,
        "selected_cards": 30,
        "selected_card_occurrences": 217,
        "complete_lexicon_rows": 569,
        "complete_ledger_rows": 776,
        "blank_or_evasive_glosses": 0,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
        "claim_ceiling": "Selected speculative source expansions, not deciphered plaintext.",
    }
    (HERE / "V17_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
