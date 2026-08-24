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
    dictionary = read("FIVE_HUNDRED_THIRTY_FOURTH_SEVENTY_NINE_F83_CARD_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_THIRTY_FOURTH_ONE_HUNDRED_FIFTY_THREE_EVENT_INTERLINEAR.tsv")
    cells = read("FIVE_HUNDRED_THIRTY_FOURTH_FIFTY_FOUR_F83_OPERATING_CELLS.tsv")
    modules = read("FIVE_HUNDRED_THIRTY_FOURTH_TEN_F83_OWNER_MODULES.tsv")
    boundaries = read("FIVE_HUNDRED_THIRTY_FOURTH_THREE_OWNER_BOUNDARY_CELLS.tsv")
    shared = read("FIVE_HUNDRED_THIRTY_FOURTH_THIRTY_SIX_PRIOR_SHARED_CARDS.tsv")
    by_card = defaultdict(set)
    for row in events:
        by_card[row["card_no"]].add(row["invariant_card_reading_de"])
    checks = {
        "dictionary79": len(dictionary) == 79 and len({row["card_no"] for row in dictionary}) == 79,
        "events153": len(events) == 153 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(229, 382)],
        "record_counts86_47_11_9": Counter(row["record"] for row in events)
        == Counter({"B3": 86, "B4": 47, "B5": 11, "B6": 9}),
        "cells54": len(cells) == 54 and len({row["statement_id"] for row in cells}) == 54,
        "closed49_open5": Counter(row["terminal"] for row in cells) == Counter({"YES": 49, "NO": 5}),
        "cell_event_partition": sum(len(row["event_ids"].split("|")) for row in cells) == 153,
        "modules10": len(modules) == 10 and sum(int(row["events"]) for row in modules) == 153,
        "module_event_counts": [int(row["events"]) for row in modules] == [10, 9, 16, 27, 24, 23, 18, 6, 11, 9],
        "boundary_cells3": [row["statement_id"] for row in boundaries] == ["B3-S016", "B3-S026", "B4-S015"],
        "no_global_cycle": all(row["global_cycle_edge"] == "NONE" for row in events)
        and all(row["global_cycle_claim"] == "NONE" for row in cells),
        "invariant_card_values": all(len(values) == 1 for values in by_card.values()),
        "shared_prior36": len(shared) == 36 and all(row["shared_with_earlier_fixed_pages"] == "YES" for row in shared),
        "no_blank_readings": all(row["minimum_source_clause_de"] for row in events)
        and all(row["complete_workshop_reading_de"] for row in cells),
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
