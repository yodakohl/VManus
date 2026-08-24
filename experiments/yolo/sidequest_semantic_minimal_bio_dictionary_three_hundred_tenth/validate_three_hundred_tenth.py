#!/usr/bin/env python3
"""Validate the minimal Biological dictionary and roundtrip recipes."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    dictionary = read("THREE_HUNDRED_TENTH_39_ENTRY_MINIMAL_BIO_DICTIONARY.tsv")
    corrections = read("THREE_HUNDRED_TENTH_SIX_WHOLE_SIGN_MODE_CORRECTIONS.tsv")
    events = read("THREE_HUNDRED_TENTH_281_EVENT_DICTIONARY_ROUNDTRIP.tsv")
    cards = read("THREE_HUNDRED_TENTH_124_CARD_PRODUCTION_RECIPES.tsv")
    entry_ids = {r["entry_id"] for r in dictionary}
    checks = {
        "dictionary_39": len(dictionary) == 39 and len(entry_ids) == 39,
        "families_26_wholes_13": sum(r["entry_type"] == "PRODUCTIVE_FAMILY" for r in dictionary) == 26 and sum(r["entry_type"] == "LEARNED_WHOLE_OR_MICROSIGN" for r in dictionary) == 13,
        "cards_124": len(cards) == 124 and len({r["master_card_id"] for r in cards}) == 124,
        "events_281": len(events) == 281 and len({r["event_id"] for r in events}) == 281,
        "recipes_resolve": all(set(r["minimal_dictionary_recipe"].split("+")) <= entry_ids for r in events + cards),
        "composed_111_whole_13": sum(r["card_layer"] == "PRODUCTIVE_COMPOSITION" for r in cards) == 111 and sum(r["card_layer"] == "LEARNED_WHOLE_OR_MICROSIGN" for r in cards) == 13,
        "six_corrections_eight_events": len(corrections) == 6 and sum(int(r["event_count"]) for r in corrections) == 8,
        "all_readings_concrete": all(r["dictionary_reading_de"].strip() for r in events),
        "no_placeholders": not any(any(token in r["dictionary_reading_de"].upper() for token in ["UNKNOWN", "EXEMPLAR", "FORMAL_LABEL"]) for r in events),
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*") if p.suffix in {".tsv", ".md"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
