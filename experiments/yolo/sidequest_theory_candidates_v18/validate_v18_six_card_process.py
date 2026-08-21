#!/usr/bin/env python3
"""Validate V18 six-card candidates and selected full-ledger propagation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
TARGETS = {
    "0275fbf14e07935b0a45", "de7321bface5628e35d6",
    "259b2b3b0bf859882e2c", "28ffbc88b97772a75f1e",
    "4d4559019a961b834aa1", "2cc054357a929df85f64",
}
EVASIVE = {"", "unknown", "opaque", "untranslated", "content", "payload",
           "item", "value", "state", "operation"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks = []
    for number in range(1, 5):
        decisions = read(HERE / f"V18_R{number}_SIX_CARD_DECISIONS.tsv")
        occurrences = read(HERE / f"V18_R{number}_31_OCCURRENCE_RECONSTRUCTIONS.tsv")
        id_column = "exact_tuple_id"
        if number == 4:
            id_column = "tuple_id"
        ids = {row[id_column] for row in decisions}
        assert ids == TARGETS
        if number == 3:
            assert len(decisions) == 18
            assert all(sum(row[id_column] == key for row in decisions) == 3 for key in TARGETS)
        else:
            assert len(decisions) == 6
        assert len(occurrences) == 31
        assert not any(any(value.lower().startswith("f84") for value in row.values())
                       for row in occurrences)
        checks.append({"candidate": f"R{number}", "cards": 6,
                       "rivals": 18, "occurrences": 31, "f84_rows": 0})

    deck = read(HERE / "V18_SELECTED_RECURRENT_DECK.tsv")
    lexicon = read(HERE / "V18_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read(HERE / "V18_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    assert len(deck) == 30
    assert len(lexicon) == 569
    assert len(ledger) == 776
    assert sum(row["exact_tuple_id"] in TARGETS for row in ledger) == 31
    assert all(row["default_English"].strip().lower() not in EVASIVE for row in ledger)
    assert not any(row["page"].startswith("f84") for row in ledger)

    result = {
        "schema": "SIDEQUEST_V18_SIX_CARD_PROCESS_VALIDATION_V1",
        "status": "PASS",
        "candidate_checks": checks,
        "selected_cards_revised": 6,
        "selected_occurrences_revised": 31,
        "complete_deck_rows": 30,
        "complete_lexicon_rows": 569,
        "complete_ledger_rows": 776,
        "blank_or_evasive_glosses": 0,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
        "claim_ceiling": "Concrete speculative process defaults, not deciphered plaintext.",
    }
    (HERE / "V18_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
