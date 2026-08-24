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
    dictionary = read("FIVE_HUNDRED_THIRTY_FIFTH_ONE_HUNDRED_TWENTY_FOUR_BIO_CARD_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_THIRTY_FIFTH_TWO_HUNDRED_EIGHTY_ONE_BIO_EVENT_INTERLINEAR.tsv")
    cells = read("FIVE_HUNDRED_THIRTY_FIFTH_NINETY_SEVEN_BIO_OPERATING_CELLS.tsv")
    modules = read("FIVE_HUNDRED_THIRTY_FIFTH_SIXTEEN_VISIBLE_OWNER_MODULES.tsv")
    recurrent = read("FIVE_HUNDRED_THIRTY_FIFTH_THIRTY_TWO_CROSS_PAGE_BIO_CARDS.tsv")
    shared = read("FIVE_HUNDRED_THIRTY_FIFTH_SEVENTEEN_HERBAL_BIO_SHARED_CARDS.tsv")
    boundaries = read("FIVE_HUNDRED_THIRTY_FIFTH_FOUR_OWNER_BOUNDARY_CELLS.tsv")
    by_card = defaultdict(set)
    for row in events:
        by_card[row["card_no"]].add(row["invariant_card_reading_de"])
    checks = {
        "dictionary124": len(dictionary) == 124 and len({row["card_no"] for row in dictionary}) == 124,
        "events281": len(events) == 281 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(101, 382)],
        "records6": Counter(row["record"] for row in events) == Counter({"B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9}),
        "pages66_62_153": Counter(row["page"] for row in events) == Counter({"f81v": 66, "f82r": 62, "f83r": 153}),
        "cells97": len(cells) == 97 and len({row["statement_id"] for row in cells}) == 97,
        "closed85_open12": Counter(row["terminal"] for row in cells) == Counter({"YES": 85, "NO": 12}),
        "cell_event_partition": sum(len(row["event_ids"].split("|")) for row in cells) == 281,
        "modules16": len(modules) == 16 and sum(int(row["events"]) for row in modules) == 281,
        "module_counts": [int(row["events"]) for row in modules] == [66, 22, 9, 5, 9, 17, 10, 9, 16, 27, 24, 23, 18, 6, 11, 9],
        "boundaries4": [row["statement_id"] for row in boundaries] == ["B2-S012", "B3-S016", "B3-S026", "B4-S015"],
        "cross_page32": len(recurrent) == 32 and sum(int(row["occurrences"]) for row in recurrent) == 176,
        "all_three12_85events": sum(row["recurs_on_all_three_bio_pages"] == "YES" for row in recurrent) == 12 and sum(int(row["occurrences"]) for row in recurrent if row["recurs_on_all_three_bio_pages"] == "YES") == 85,
        "herbal_shared17": len(shared) == 17 and all(row["shared_with_herbal"] == "YES" for row in shared),
        "invariant_values": all(len(values) == 1 for values in by_card.values()),
        "no_global_network": all(row["global_network_edge"] == "NONE" for row in events) and all(row["global_network_claim"] == "NONE" for row in cells),
        "no_blank_readings": all(row["minimum_source_clause_de"] for row in events) and all(row["complete_workshop_reading_de"] for row in cells),
        "fixed_pages_only": {row["page"] for row in events} == {"f81v", "f82r", "f83r"},
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTY_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
