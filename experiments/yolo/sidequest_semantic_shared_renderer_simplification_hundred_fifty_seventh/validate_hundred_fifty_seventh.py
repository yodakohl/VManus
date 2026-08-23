#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    surfaces = rows("HUNDRED_FIFTY_SEVENTH_103_SHARED_SURFACES.tsv")
    families = rows("HUNDRED_FIFTY_SEVENTH_47_SHARED_FAMILIES.tsv")
    choices = rows("HUNDRED_FIFTY_SEVENTH_FIVE_HAND_SHARED_COPYBOOK.tsv")
    events = rows("HUNDRED_FIFTY_SEVENTH_251_SHARED_EVENT_RENDER_TRACE.tsv")
    registered = {row["visible_surface"] for row in surfaces}
    checks = {
        "surfaces_103": len(surfaces) == 103,
        "families_47": len(families) == 47,
        "multi_33": sum(int(row["surface_count"]) > 1 for row in families) == 33,
        "single_14": sum(int(row["surface_count"]) == 1 for row in families) == 14,
        "habits_5": len({row["five_habit_class"] for row in surfaces}) == 5,
        "profile_choices_235": len(choices) == 235,
        "five_profiles": len({row["profile"] for row in choices}) == 5,
        "all_choices_registered": all(row["chosen_surface"] in registered and row["registered_surface"] == "YES" for row in choices),
        "shared_events_251": len(events) == 251,
        "all_events_recover": all(row["master_recovery"] == "EXACT" for row in events),
        "semantic_changes_none": all(row["semantic_change"] == "NONE" for row in families),
        "no_empty_cells": all(all(v for v in row.values()) for table in (surfaces, families, choices, events) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
