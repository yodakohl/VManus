#!/usr/bin/env python3
"""Validate the bounded V21 Astro consultation artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    zodiac = read("V21_ZODIAC_BODY_SELECTOR.tsv")
    stations = read("V21_28_STATION_CONSULTATION.tsv")
    lexicon = read("V21_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read("V21_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    assert len(zodiac) == 12
    assert len({row["working_owner"] for row in zodiac}) == 12
    assert len(stations) == 28
    assert all(row["cross_page_alignment"] ==
               "NOT_VISIBLE_CONVENTIONAL_INDEX_REQUIRED" for row in stations)
    assert len(lexicon) == 569
    assert len(ledger) == 776
    assert sum(row["page"] in {"f67r2", "f68r1", "f69v"} for row in ledger) == 395
    assert not any(row["page"].startswith("f84") for row in ledger)
    result = {
        "schema": "SIDEQUEST_V21_ASTRO_CONSULTATION_VALIDATION_V1",
        "status": "PASS",
        "astro_events": 395,
        "zodiac_body_rows": 12,
        "station_working_rows": 28,
        "visible_cross_page_station_alignment": 0,
        "complete_lexicon_rows": 569,
        "complete_ledger_rows": 776,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
        "claim_ceiling": "Speculative consultation mechanism, not decoded astronomy.",
    }
    (HERE / "V21_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
