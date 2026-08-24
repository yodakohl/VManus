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
    events = read("FOUR_HUNDRED_FIFTY_FIFTH_100_EVENT_ALIGNMENT.tsv")
    statements = read("FOUR_HUNDRED_FIFTY_FIFTH_19_CONTROLLED_STATEMENTS.tsv")
    articles = read("FOUR_HUNDRED_FIFTY_FIFTH_FIVE_CONTINUOUS_ARTICLES.tsv")
    nouns = read("FOUR_HUNDRED_FIFTY_FIFTH_SUPPLIED_NOUN_AUDIT.tsv")
    prose = " ".join(row["controlled_fluent_reading_de"].lower() for row in statements)
    banned = ["wurzel", "blüte", "blumen", "kraut", "geschwür", "schwellung", "wein", "husten", "krankheit", "magen", "darm", "honig", "öl"]
    checks = {
        "events_100": len(events) == 100,
        "event_order": [row["event_id"] for row in events] == [f"E{n:03d}" for n in range(1, 101)],
        "statements_19": len(statements) == 19,
        "articles_5": len(articles) == 5,
        "record_counts": [int(row["events"]) for row in articles] == [14, 24, 17, 18, 27],
        "statement_events_once": sorted((event for row in statements for event in row["event_ids"].split("|")), key=lambda item: int(item[1:])) == [f"E{n:03d}" for n in range(1, 101)],
        "event_statement_match": all(next(row for row in statements if row["statement_id"] == event["statement_id"])["controlled_fluent_reading_de"] == event["statement_fluent_reading_de"] for event in events),
        "no_discarded_nouns": not any(word in prose for word in banned),
        "noun_licenses_15": len(nouns) == 15 and all(row["license"] for row in nouns),
        "no_smuggling_flags": all(row["discarded_content_reintroduced"] == "NO" for row in statements),
        "picture_owners_4": len({row["picture_owner"] for row in events}) == 4,
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
