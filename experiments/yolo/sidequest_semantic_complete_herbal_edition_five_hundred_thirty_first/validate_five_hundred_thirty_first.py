#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    dictionary = read("FIVE_HUNDRED_THIRTY_FIRST_SIXTY_SIX_CARD_HERBAL_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_THIRTY_FIRST_ONE_HUNDRED_EVENT_INTERLINEAR.tsv")
    statements = read("FIVE_HUNDRED_THIRTY_FIRST_NINETEEN_STATEMENT_EDITION.tsv")
    articles = read("FIVE_HUNDRED_THIRTY_FIRST_FOUR_COMPLETE_HERBAL_ARTICLES.tsv")
    cross = read("FIVE_HUNDRED_THIRTY_FIRST_TEN_CROSS_RECORD_CARDS.tsv")
    primitives = read("FIVE_HUNDRED_THIRTY_FIRST_HERBAL_PRIMITIVE_PROFILE.tsv")
    by_card = defaultdict(set)
    for row in events:
        by_card[row["card_no"]].add(row["invariant_card_reading_de"])
    checks = {
        "dictionary66": len(dictionary) == 66 and len({row["card_no"] for row in dictionary}) == 66,
        "events100": len(events) == 100 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 101)],
        "record_counts14_24_17_18_27": Counter(row["record"] for row in events)
        == Counter({"H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27}),
        "statements19": len(statements) == 19 and len({row["statement_id"] for row in statements}) == 19,
        "articles4": len(articles) == 4 and sum(int(row["events"]) for row in articles) == 100,
        "pages4": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"},
        "invariant_card_values": all(len(values) == 1 for values in by_card.values()),
        "dictionary_event_counts": sum(int(row["occurrences"]) for row in dictionary) == 100,
        "no_blank_source_clauses": all(row["minimum_source_clause_de"] for row in events),
        "statement_event_partition": sum(len(row["event_ids"].split("|")) for row in statements) == 100,
        "cross_record_cards10": len(cross) == 10 and all(row["cross_record"] == "YES" for row in cross),
        "aiin_measure9": next(row for row in dictionary if row["card_no"] == "PROC009")["occurrences"] == "9",
        "primitives8": len(primitives) == 8 and sum(int(row["total"]) for row in primitives) == 104,
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events + articles),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
