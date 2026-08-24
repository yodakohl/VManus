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
    dictionary = read("FIVE_HUNDRED_THIRTY_SECOND_FORTY_THREE_B1_CARD_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_THIRTY_SECOND_SIXTY_SIX_B1_EVENT_INTERLINEAR.tsv")
    cells = read("FIVE_HUNDRED_THIRTY_SECOND_TWENTY_ONE_B1_OPERATING_CELLS.tsv")
    modules = read("FIVE_HUNDRED_THIRTY_SECOND_SEVEN_B1_POOL_MODULES.tsv")
    shared = read("FIVE_HUNDRED_THIRTY_SECOND_TEN_HERBAL_SHARED_CARDS.tsv")
    by_card = defaultdict(set)
    for row in events:
        by_card[row["card_no"]].add(row["invariant_card_reading_de"])
    checks = {
        "dictionary43": len(dictionary) == 43 and len({row["card_no"] for row in dictionary}) == 43,
        "events66": len(events) == 66 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(101, 167)],
        "cells21": len(cells) == 21 and len({row["statement_id"] for row in cells}) == 21,
        "closed17_open4": Counter(row["terminal"] for row in cells) == Counter({"YES": 17, "NO": 4}),
        "cell_event_partition": sum(len(row["event_ids"].split("|")) for row in cells) == 66,
        "modules7": len(modules) == 7 and sum(int(row["events"]) for row in modules) == 66,
        "owner_constant": {row["owner_id"] for row in events} == {"B1_SHARED_TWO_ROW_POOL"},
        "no_global_flow": all(row["global_flow_direction"] == "NONE" for row in events)
        and all(row["module_relation"] == "LOCAL_MODULE_WITHOUT_GLOBAL_FLOW_ORDER" for row in modules),
        "invariant_card_values": all(len(values) == 1 for values in by_card.values()),
        "shared_herbal10": len(shared) == 10 and all(row["shared_with_herbal"] == "YES" for row in shared),
        "no_blank_readings": all(row["minimum_source_clause_de"] for row in events)
        and all(row["fluent_pool_reading_de"] for row in cells),
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events + modules),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
