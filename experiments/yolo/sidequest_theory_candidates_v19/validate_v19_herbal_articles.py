#!/usr/bin/env python3
"""Validate the four V19 candidates and selected full-ledger propagation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EVASIVE = {"", "unknown", "opaque", "untranslated", "content", "payload",
           "item", "value", "state", "operation"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    candidates = []
    for number in range(1, 5):
        dictionary = read(HERE / f"V19_R{number}_HERBAL_CARD_DICTIONARY.tsv")
        events = read(HERE / f"V19_R{number}_100_EVENT_INTERLINEAR.tsv")
        alternatives = read(HERE / f"V19_R{number}_SINGLETON_ALTERNATIVES.tsv")
        assert len(dictionary) == 66
        assert len({next(iter(row.values())) for row in dictionary}) == 66
        assert len(events) == 100
        assert len(alternatives) == 55
        assert not any(any(value.lower().startswith("f84") for value in row.values())
                       for row in events)
        candidates.append({"candidate": f"R{number}", "types": 66,
                           "events": 100, "singleton_alternatives": 55})

    selected_dictionary = read(HERE / "V19_SELECTED_HERBAL_DICTIONARY.tsv")
    selected_events = read(HERE / "V19_SELECTED_100_EVENT_INTERLINEAR.tsv")
    lexicon = read(HERE / "V19_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read(HERE / "V19_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    assert len(selected_dictionary) == 66
    assert len(selected_events) == 100
    assert sum(row["selection_scope"] == "V19_HERBAL_ONLY_R2"
               for row in selected_dictionary) == 49
    assert sum(row["selection_scope"] == "V18_CROSS_REGISTER_PRESERVED"
               for row in selected_dictionary) == 17
    assert len(lexicon) == 569
    assert len(ledger) == 776
    assert all(row["default_English"].strip().lower() not in EVASIVE for row in ledger)
    assert not any(row["page"].startswith("f84") for row in ledger)

    result = {
        "schema": "SIDEQUEST_V19_COMPLETE_HERBAL_ARTICLE_VALIDATION_V1",
        "status": "PASS",
        "candidate_checks": candidates,
        "selected_candidate": "R2_WITH_V18_CROSS_REGISTER_PRESERVATION",
        "herbal_types": 66,
        "herbal_events": 100,
        "herbal_only_types_revised": 49,
        "cross_register_types_preserved": 17,
        "complete_lexicon_rows": 569,
        "complete_ledger_rows": 776,
        "blank_or_evasive_glosses": 0,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
        "claim_ceiling": "Complete speculative English defaults, not deciphered plaintext.",
    }
    (HERE / "V19_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
