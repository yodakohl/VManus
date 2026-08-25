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
    pages = read("SEVEN_HUNDRED_SEVENTY_SIXTH_7_PAGE_HAND_MAP.tsv")
    profiles = read("SEVEN_HUNDRED_SEVENTY_SIXTH_2_ACTUAL_HAND_PROFILES.tsv")
    special = read("SEVEN_HUNDRED_SEVENTY_SIXTH_7_HAND_LOCAL_SPECIAL_CARDS.tsv")
    trace = read("SEVEN_HUNDRED_SEVENTY_SIXTH_381_HAND_ACCESS_TRACE.tsv")
    ecology = read("SEVEN_HUNDRED_SEVENTY_SIXTH_3_HAND_CARD_ECOLOGIES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_SIXTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    page_hand = {row["page"]: row["hand"] for row in pages}
    profile = {row["hand"]: row for row in profiles}
    checks = {
        "counts_7_2_7_381_3": (len(pages), len(profiles), len(special), len(trace), len(ecology)) == (7, 2, 7, 381, 3),
        "page_events381": sum(int(row["events"]) for row in pages) == 381,
        "page_statements116": sum(int(row["statements"]) for row in pages) == 116,
        "hand1_pages": {page for page, hand in page_hand.items() if hand == "HAND_1"} == {"f10r", "f11r", "f56r"},
        "hand2_pages": {page for page, hand in page_hand.items() if hand == "HAND_2"} == {"f55v", "f81v", "f82r", "f83r"},
        "hand_events_82_299": (int(profile["HAND_1"]["events"]), int(profile["HAND_2"]["events"])) == (82, 299),
        "hand_statements_15_101": (int(profile["HAND_1"]["statements"]), int(profile["HAND_2"]["statements"])) == (15, 101),
        "component_loads_35_37": (int(profile["HAND_1"]["component_inventory"]), int(profile["HAND_2"]["component_inventory"])) == (35, 37),
        "special_cards_do_not_cross": all("," not in row["hands"] for row in special),
        "hand1_special_os_cfh": {row["exact_card_id"] for row in special if row["hands"] == "HAND_1"} == {"PROC005", "PROC028"},
        "hand2_special_talam_ld_da_lsh": {row["exact_card_id"] for row in special if row["hands"] == "HAND_2"} == {"PROC043", "PROC084", "PROC086", "PROC155", "PROC169"},
        "trace_exact_and_available": [row["event_id"] for row in trace] == [f"E{i:03d}" for i in range(1, 382)] and all(row["available_to_actual_hand"] == "YES" for row in trace),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (pages, profiles, special, trace, ecology) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["special_cards_crossing_hands"] == 0,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
