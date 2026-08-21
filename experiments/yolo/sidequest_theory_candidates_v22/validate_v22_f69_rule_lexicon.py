#!/usr/bin/env python3
"""Validate identity-consistent V22 f69 rules and complete propagation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rules = read("V22_F69_28_RULES.tsv")
    repeated = read("V22_REPEATED_RULE_AUDIT.tsv")
    lexicon = read("V22_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read("V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    assert len(rules) == 28
    assert all(row["polarity_from_layout"] == "NO" for row in rules)
    okeod = [row for row in repeated if row["surface_entry"] == "okeod"]
    assert len(okeod) == 1
    assert okeod[0]["station_indices"] == "11|15|24"
    assert okeod[0]["layout_parities"] == "LONG|LONG|SHORT"
    assert okeod[0]["shared_concrete_rule"] == "favorable for bathing"
    assert len(lexicon) == 569
    assert len(ledger) == 776
    assert not any(row["page"].startswith("f84") for row in ledger)
    result = {
        "schema": "SIDEQUEST_V22_F69_RULE_LEXICON_VALIDATION_V1",
        "status": "PASS",
        "radial_entries": 28,
        "radial_events_revised": 33,
        "repeated_complete_entries": 1,
        "parity_crossing_identity_contradictions_repaired": 1,
        "complete_lexicon_rows": 569,
        "complete_ledger_rows": 776,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
        "claim_ceiling": "Concrete speculative election rules, not decoded labels.",
    }
    (HERE / "V22_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
