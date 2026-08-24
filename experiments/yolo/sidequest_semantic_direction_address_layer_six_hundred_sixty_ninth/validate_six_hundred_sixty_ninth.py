#!/usr/bin/env python3
"""Validate the shared direction/address layer."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("SIX_HUNDRED_SIXTY_NINTH_85_DIRECTION_CARDS.tsv")
    events = read("SIX_HUNDRED_SIXTY_NINTH_146_DIRECTION_EVENTS.tsv")
    roots = read("SIX_HUNDRED_SIXTY_NINTH_6_ROOT_SUMMARY.tsv")
    contrasts = read("SIX_HUNDRED_SIXTY_NINTH_5_MINIMAL_CONTRASTS.tsv")
    expected = {"L": (18, 27), "OL": (25, 48), "OT": (16, 26), "AL": (22, 39), "AR": (10, 14), "AIR": (5, 5)}
    checks = {
        "eighty_five_union_cards": len(cards) == 85,
        "one_hundred_forty_six_union_events": len(events) == 146,
        "six_roots": len(roots) == 6 and {row["root"] for row in roots} == set(expected),
        "raw_root_counts": all((int(row["card_types"]), int(row["events"])) == expected[row["root"]] for row in roots),
        "five_contrasts": len(contrasts) == 5,
        "unique_event_rows": len({row["event_id"] for row in events}) == 146,
        "all_cards_have_root_contribution": all(row["selected_roots"] and row["portable_contributions_de"] for row in cards),
        "all_events_have_root_contribution": all(row["selected_roots"] and row["portable_contributions_de"] for row in events),
        "ar_al_distinct": next(row for row in roots if row["root"] == "AR")["portable_value_de"] != next(row for row in roots if row["root"] == "AL")["portable_value_de"],
        "air_not_ar": next(row for row in roots if row["root"] == "AIR")["portable_value_de"] != next(row for row in roots if row["root"] == "AR")["portable_value_de"],
        "all_closes_terminal": all(row["statement_position"] in {"FINAL", "WHOLE"} for row in events if row["contains_close"] == "YES"),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
