#!/usr/bin/env python3
"""Validate Pass 763 workshop curriculum."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_SIXTY_THIRD_39_COMPONENT_LESSONS.tsv")
    cards = read("SEVEN_HUNDRED_SIXTY_THIRD_173_CARD_SPECIALIZATION.tsv")
    rules = read("SEVEN_HUNDRED_SIXTY_THIRD_9_RULE_CURRICULUM.tsv")
    tokens = read("SEVEN_HUNDRED_SIXTY_THIRD_27_MOTIF_TAIL_ASSIGNMENT.tsv")
    lessons = read("SEVEN_HUNDRED_SIXTY_THIRD_14_LESSON_CURRICULUM.tsv")
    roles = read("SEVEN_HUNDRED_SIXTY_THIRD_4_SCRIBE_ROLES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    decks = {name: [row for row in cards if row["deck_assignment"] == name] for name in {row["deck_assignment"] for row in cards}}
    role = {row["role"]: row for row in roles}
    checks = {
        "counts_39_173_9_27_14_4": (len(components), len(cards), len(rules), len(tokens), len(lessons), len(roles)) == (39, 173, 9, 27, 14, 4),
        "component_ranks_1_to_39": [int(row["rank"]) for row in components] == list(range(1, 40)),
        "deck_partition_17_49_107": sorted(len(rows) for rows in decks.values()) == [17, 49, 107],
        "common_deck_136_events": sum(int(row["events"]) for row in decks["COMMON_17_CARD_DECK"]) == 136,
        "card_events_381": sum(int(row["events"]) for row in cards) == 381,
        "tokens_5_shared_9_herbal_13_bio": (sum(row["scope"] == "COMMON_HERBAL_BIO" for row in tokens), sum(row["scope"] == "HERBAL_SPECIALIST" for row in tokens), sum(row["scope"] == "BIO_SPECIALIST" for row in tokens)) == (5, 9, 13),
        "hours_114_74_84_24": (int(role["MASTER_CORRECTOR"]["curriculum_hours"]), int(role["HERBAL_SCRIBE"]["curriculum_hours"]), int(role["BIO_STATION_SCRIBE"]["curriculum_hours"]), int(role["ASTRO_TABLE_SCRIBE"]["curriculum_hours"])) == (114, 74, 84, 24),
        "specialist_card_loads_66_124": (int(role["HERBAL_SCRIBE"]["exact_cards"]), int(role["BIO_STATION_SCRIBE"]["exact_cards"])) == (66, 124),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (components, cards, rules, tokens, lessons, roles) for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
