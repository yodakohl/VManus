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
    events = read("FOUR_HUNDRED_TWENTY_FIFTH_HERBAL_100_EVENT_EDITION.tsv")
    articles = read("FOUR_HUNDRED_TWENTY_FIFTH_FIVE_COMPLETE_ARTICLES.tsv")
    grammar = read("FOUR_HUNDRED_TWENTY_FIFTH_EIGHT_COMMON_GRAMMAR_FAMILIES.tsv")
    weak = read("FOUR_HUNDRED_TWENTY_FIFTH_FIVE_WEAKEST_CARDS.tsv")
    checks = {
        "one_hundred_events": len(events) == 100,
        "event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 101)],
        "every_event_once": len({row["event_id"] for row in events}) == 100,
        "every_value_nonempty": all(row["small_value_de"] for row in events),
        "five_articles": len(articles) == 5,
        "article_event_sum": sum(int(row["events"]) for row in articles) == 100,
        "eight_grammar_families": len(grammar) == 8,
        "mass_all_articles": [row for row in grammar if row["family"] == "AIIN"][0]["records"] == "H1|H2|H3|H4|H5",
        "y_all_articles": [row for row in grammar if row["family"] == "Y_CURRENT_OR_REFERENT"][0]["records"] == "H1|H2|H3|H4|H5",
        "five_weak_cards": len(weak) == 5 and {row["record"] for row in weak} == {"H1", "H2", "H3", "H4", "H5"},
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (events, articles, grammar, weak) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
