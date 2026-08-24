#!/usr/bin/env python3
"""Validate the complete B3 four-desk commission."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_third.py")], check=True)
    events = read("SIX_HUNDRED_NINETY_THIRD_86_EVENT_DESK_TRACE.tsv")
    statements = read("SIX_HUNDRED_NINETY_THIRD_34_STATEMENT_HANDOFFS.tsv")
    loci = read("SIX_HUNDRED_NINETY_THIRD_10_LOCUS_COPY_SHEETS.tsv")
    composites = read("SIX_HUNDRED_NINETY_THIRD_5_COMPOSITE_JUNCTION_CARDS.tsv")
    handoffs = read("SIX_HUNDRED_NINETY_THIRD_6_PACKET_HANDOFFS.tsv")
    counts = Counter(row["selected_by_desk"] for row in events)
    checks = {
        "eighty_six_events": len(events) == 86,
        "event_ids_consecutive": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(229, 315)],
        "thirty_four_statements": len(statements) == 34,
        "all_events_in_statements": sum(int(row["events"]) for row in statements) == 86,
        "ten_physical_loci": len(loci) == 10 and sum(int(row["events"]) for row in loci) == 86,
        "five_visible_owners": len({row["owner_de"] for row in events}) == 5,
        "desk_card_counts": counts == Counter({"S01_MASTER_CORRECTOR": 39, "S02_PREPARATION_WET": 5, "S03_TRANSFER": 25, "S04_STATE_CONTROL": 17}),
        "five_composite_cards": len(composites) == 5 and {row["event_id"] for row in composites} == {"E248", "E250", "E296", "E300", "E303"},
        "whole_cards_never_split": all(row["final_inscription_by"] == "S01_MASTER_FINAL_COPY" for row in events),
        "two_owner_break_statements": sum(row["owner_break_inside_statement"] == "YES" for row in statements) == 2,
        "six_packet_handoffs": len(handoffs) == 6,
        "all_surfaces_present": all(row["surface"] and row["full_recipe"] for row in events),
        "one_final_copy_hand": len({row["final_inscription_by"] for row in events}) == 1,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
    }
    (HERE / "SIX_HUNDRED_NINETY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
