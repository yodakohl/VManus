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
    cards = read("SEVEN_HUNDRED_SEVENTY_EIGHTH_12_SHARED_CARD_VARIANTS.tsv")
    events = read("SEVEN_HUNDRED_SEVENTY_EIGHTH_106_SHARED_CARD_EVENTS.tsv")
    recipes = read("SEVEN_HUNDRED_SEVENTY_EIGHTH_13_SHARED_RECIPE_REALIZATIONS.tsv")
    crossover = read("SEVEN_HUNDRED_SEVENTY_EIGHTH_3_HERBAL_CROSSOVER_CARDS.tsv")
    profiles = read("SEVEN_HUNDRED_SEVENTY_EIGHTH_4_WRAPPER_PROFILES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    profile = {row["profile"]: row for row in profiles}
    crossover_map = {row["component_recipe"]: row for row in crossover}
    checks = {
        "counts_12_106_13_3_4": (len(cards), len(events), len(recipes), len(crossover), len(profiles)) == (12, 106, 13, 3, 4),
        "shared_recipe_events114": sum(int(row["hand_1_events"]) + int(row["hand_2_events"]) for row in recipes) == 114,
        "six_disjoint_surface_cards": sum(row["surface_overlap"] == "NONE" for row in cards) == 6,
        "one_disjoint_exact_recipe": [row["component_recipe"] for row in recipes if row["relationship"] == "DISJOINT_EXACT_CARD_ALTERNANTS"] == ["OK+OL"],
        "f55_or_y_bare": crossover_map["OR"]["f55v_nonentry_bare"] == "1" and crossover_map["Y"]["f55v_nonentry_bare"] == "1",
        "hand1_or_y_not_bare": crossover_map["OR"]["hand_1_nonentry_bare"] == "0" and crossover_map["Y"]["hand_1_nonentry_bare"] == "0",
        "shared_bare_rates_4of33_13of48": (profile["HAND_1_ALL_SHARED_CARDS"]["eligible_events"], profile["HAND_1_ALL_SHARED_CARDS"]["bare_events"], profile["HAND_2_ALL_SHARED_CARDS"]["eligible_events"], profile["HAND_2_ALL_SHARED_CARDS"]["bare_events"]) == ("33", "4", "48", "13"),
        "event_ids_unique": len({row["event_id"] for row in events}) == 106,
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (cards, events, recipes, crossover, profiles) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["shared_recipe_events"] == 114,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
