#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("FOUR_HUNDRED_SIXTIETH_381_EVENT_CURRENT_INTERLINEAR.tsv")
    cards = read("FOUR_HUNDRED_SIXTIETH_173_CARD_CURRENT_DICTIONARY.tsv")
    statements = read("FOUR_HUNDRED_SIXTIETH_116_STATEMENT_CURRENT_EDITION.tsv")
    articles = read("FOUR_HUNDRED_SIXTIETH_FIVE_HERBAL_ARTICLES.tsv")
    procedures = read("FOUR_HUNDRED_SIXTIETH_24_BIOLOGICAL_PROCEDURES.tsv")
    sections = read("FOUR_HUNDRED_SIXTIETH_29_SECTION_WORKSHOP_EDITION.tsv")
    transitions = read("FOUR_HUNDRED_SIXTIETH_SEVEN_VISIBLE_SCENE_TRANSITIONS.tsv")
    displayed = " ".join(row["current_fluent_reading_de"] for row in statements).lower()
    banned = re.compile(r"\b(?:dasselbe|denselben|tuch|warm|roh|rohansatz)\b", re.IGNORECASE)
    checks = {
        "events_381": len(events) == 381,
        "cards_173": len(cards) == 173,
        "statements_116": len(statements) == 116,
        "articles_5": len(articles) == 5 and sum(int(row["events"]) for row in articles) == 100,
        "procedures_24": len(procedures) == 24 and sum(int(row["events"]) for row in procedures) == 281,
        "sections_29": len(sections) == 29,
        "section_events_once": sorted((event for row in sections for event in row["event_ids"].split("|")), key=lambda item: int(item[1:])) == [f"E{n:03d}" for n in range(1, 382)],
        "statement_events_once": sorted((event for row in statements for event in row["event_ids"].split("|")), key=lambda item: int(item[1:])) == [f"E{n:03d}" for n in range(1, 382)],
        "record_count_11": len({row["record_unit_id"] for row in statements}) == 11,
        "scene_transitions_7": len(transitions) == 7,
        "overrides_8": sum(row["pass460_override"] == "YES" for row in statements) == 8,
        "no_superseded_display_words": banned.search(displayed) is None,
        "line_not_sentence": all(row["physical_line_is_sentence_boundary"] == "NO" for row in statements),
        "productive_372_whole_9": [sum(row["lexicon_class"] == kind for row in events) for kind in ("PRODUCTIVE_COMPOSITION", "MEMORIZED_WHOLE_CARD")] == [372, 9],
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
