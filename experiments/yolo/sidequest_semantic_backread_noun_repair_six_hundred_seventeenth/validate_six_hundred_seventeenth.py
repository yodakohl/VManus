#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    words = read("SIX_HUNDRED_SEVENTEENTH_39_SHARP_WORDS.tsv")
    cards = read("SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv")
    events = read("SIX_HUNDRED_SEVENTEENTH_381_SHARP_EVENT_COMMANDS.tsv")
    statements = read("SIX_HUNDRED_SEVENTEENTH_116_SHARP_BACKREADS.tsv")
    drawers = read("SIX_HUNDRED_SEVENTEENTH_4_SHARP_DRAWERS.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    expected = {"SOLLMASS", "FLUESSIGKEITSLAUF", "ZIELSTELLE", "VORRAT", "DURCHLASSKANAL", "ZWEITMARKER", "ZUTAT", "ARBEITSSTUFE", "ARBEITSFACH", "ARBEITSPOSTEN"}
    checks = {
        "words39": len(words) == 39 and len({row["canonical_component"] for row in words}) == 39,
        "ten_repairs": sum(row["noun_address_revision"] == "YES" for row in words) == 10,
        "new_words_exact": {row["spoken_workshop_word_de"] for row in words if row["noun_address_revision"] == "YES"} == expected,
        "cards173": len(cards) == 173 and len(card_by_id) == 173,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "event_card_match": all(row["standard_command_de"] == card_by_id[row["card_no"]]["standard_command_de"] for row in events),
        "statements116": len(statements) == 116 and sum(int(row["event_count"]) for row in statements) == 381,
        "drawers4": len(drawers) == 4,
        "commands163": len({(row["semantic_component_parse"], row["standard_command_de"]) for row in cards}) == 163,
        "all_backreads": all(row["sharp_controlled_backread_de"].strip() for row in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
