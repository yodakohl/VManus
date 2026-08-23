#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    candidates = rows("HUNDRED_SIXTY_EIGHTH_4_HERBAL_SOURCE_CANDIDATES.tsv")
    bridges = rows("HUNDRED_SIXTY_EIGHTH_3_EXACT_H3_B4_BRIDGES.tsv")
    scenario = rows("HUNDRED_SIXTY_EIGHTH_53_EVENT_H3_TO_B4_SCENARIO.tsv")
    checks = {
        "candidates_4": len(candidates) == 4,
        "one_selected": sum(row["selection"] == "SELECTED" for row in candidates) == 1,
        "H3_selected": any(row["article_id"] == "B_F11R_CLEAR_EXTRACT_ARTICLE" and row["selection"] == "SELECTED" for row in candidates),
        "H4_strong_rival": any(row["article_id"] == "C_F55V_PORTIONED_PREPARATION_ARTICLE" and row["selection"] == "STRONG_RIVAL" for row in candidates),
        "bridges_3": len(bridges) == 3,
        "exact_shey_bridge": any(row["master_card_id"] == "MC119" and row["H3_surfaces"] == "shey" and row["B4_surfaces"] == "shey" for row in bridges),
        "scenario_53": len(scenario) == 53,
        "H3_events_17": sum(row["source_record"] == "H3" for row in scenario) == 17,
        "B4_events_36": sum(row["source_record"] == "B4" for row in scenario) == 36,
        "combined_order_complete": [int(row["combined_order"]) for row in scenario] == list(range(1, 54)),
        "fixed_pages": {row["page"] for row in scenario} == {"f11r", "f83r"},
        "no_empty_cells": all(all(value for value in row.values()) for table in (candidates, bridges, scenario) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
