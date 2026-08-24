#!/usr/bin/env python3
"""Validate the fresh board-composed work order."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLOT_RANK = {"S1_BEZUG_FOLGE": 1, "S2_MATERIAL_MASS": 2, "S3_PROZESS_TRANSFER": 3, "S4_DAUER_ZUSTAND": 4, "S5_ZIEL_ANWENDUNG": 5, "S6_BEREIT_ABSCHLUSS": 6}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read_tsv("THREE_HUNDRED_FIFTY_FOURTH_FRESH_ELEVEN_CARD_WORK_ORDER.tsv")
    cycles = read_tsv("THREE_HUNDRED_FIFTY_FOURTH_FOUR_MICROCYCLES.tsv")
    dependencies = read_tsv("THREE_HUNDRED_FIFTY_FOURTH_EXEMPLAR_DEPENDENCY.tsv")
    dep = {row["dependency"]: int(row["events"]) for row in dependencies}
    by_cycle = {}
    for row in events:
        by_cycle.setdefault(row["microcycle"], []).append(row)
    checks = {
        "eleven_events": len(events) == 11,
        "eleven_unique_cards": len({row["joint_tuple_id"] for row in events}) == 11,
        "four_cycles": len(cycles) == 4 and set(by_cycle) == {"1", "2", "3", "4"},
        "two_owners": len({row["owner"] for row in events}) == 2,
        "five_states": len({row["incoming_state"] for row in events} | {row["outgoing_state"] for row in events}) == 5,
        "slot_order_forward": all([SLOT_RANK[row["slot_code"]] for row in rows] == sorted(SLOT_RANK[row["slot_code"]] for row in rows) for rows in by_cycle.values()),
        "state_thread_continuous": all(events[i]["outgoing_state"] == events[i + 1]["incoming_state"] for i in range(len(events) - 1)),
        "all_values_and_ids_attested": all(row["value_and_identity_attested"] == "YES" for row in events),
        "no_running_page_exemplar": all(row["running_page_exemplar_needed"] == "NO" for row in events) and dep["RUNNING_PAGE_EXEMPLAR"] == 0,
        "dependency_counts_8_2_1": dep["BOARD_PRODUCTIVE_RULE"] == 8 and dep["PAIR_PLACARD_P13"] + dep["PAIR_PLACARD_P07"] == 2 and dep["OWNER_PINNED_MASTER_CARD_T11"] == 1,
        "hand_c_surfaces_complete": all(row["hand_c_surface"] for row in events),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
