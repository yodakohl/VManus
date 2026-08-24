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
    dictionary = read("FIVE_HUNDRED_THIRTY_THIRD_FORTY_SIX_B2_CARD_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_THIRTY_THIRD_SIXTY_TWO_B2_EVENT_INTERLINEAR.tsv")
    cells = read("FIVE_HUNDRED_THIRTY_THIRD_TWENTY_TWO_B2_OPERATING_CELLS.tsv")
    stations = read("FIVE_HUNDRED_THIRTY_THIRD_FIVE_B2_STATIONS.tsv")
    shared = read("FIVE_HUNDRED_THIRTY_THIRD_FIFTEEN_PRIOR_SHARED_CARDS.tsv")
    by_card = defaultdict(set)
    for row in events:
        by_card[row["card_no"]].add(row["invariant_card_reading_de"])
    checks = {
        "dictionary46": len(dictionary) == 46 and len({row["card_no"] for row in dictionary}) == 46,
        "events62": len(events) == 62 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(167, 229)],
        "cells22": len(cells) == 22 and len({row["statement_id"] for row in cells}) == 22,
        "closed19_open3": Counter(row["terminal"] for row in cells) == Counter({"YES": 19, "NO": 3}),
        "cell_event_partition": sum(len(row["event_ids"].split("|")) for row in cells) == 62,
        "stations5": len(stations) == 5
        and [int(row["events"]) for row in stations] == [22, 9, 5, 9, 17]
        and sum(int(row["events"]) for row in stations) == 62,
        "owners5": len({row["visible_owner_id"] for row in events}) == 5,
        "one_cross_owner_statement": [row["statement_id"] for row in cells if row["crosses_visible_owner_boundary"] == "YES"] == ["B2-S012"],
        "no_global_network": all(row["global_network_edge"] == "NONE" for row in events)
        and all(row["global_network_claim"] == "NONE" for row in cells),
        "invariant_card_values": all(len(values) == 1 for values in by_card.values()),
        "shared_prior15": len(shared) == 15 and all(row["shared_with_herbal_or_b1"] == "YES" for row in shared),
        "no_blank_readings": all(row["minimum_source_clause_de"] for row in events)
        and all(row["fluent_station_reading_de"] for row in cells),
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
