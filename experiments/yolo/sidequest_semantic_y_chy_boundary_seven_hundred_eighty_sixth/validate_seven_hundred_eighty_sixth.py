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
    recipes = read("SEVEN_HUNDRED_EIGHTY_SIXTH_53_OPEN_Y_RECIPES.tsv")
    events = read("SEVEN_HUNDRED_EIGHTY_SIXTH_122_OPEN_Y_EVENTS.tsv")
    chy = read("SEVEN_HUNDRED_EIGHTY_SIXTH_13_TERMINAL_CHY_EVENTS.tsv")
    semantic = read("SEVEN_HUNDRED_EIGHTY_SIXTH_4_SEMANTIC_CH_CONTROLS.tsv")
    rules = read("SEVEN_HUNDRED_EIGHTY_SIXTH_5_Y_CHY_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_SIXTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_53_122_13_4_5": (len(recipes), len(events), len(chy), len(semantic), len(rules)) == (53, 122, 13, 4, 5),
        "cards58": len({row["exact_card_id"] for row in events}) == 58,
        "chy_roles_12_1": (sum(row["terminal_ch_role"] == "NONSEMANTIC_CHY_REFERENT_ALLOGRAPH" for row in chy), sum(row["terminal_ch_role"] == "SEMANTIC_CH_ENTNEHMEN_PLUS_Y_REFERENT" for row in chy)) == (12, 1),
        "semantic_collision_lchy": [(row["surface"], row["component_recipe"], row["working_reading_de"]) for row in chy if row["terminal_ch_role"] == "SEMANTIC_CH_ENTNEHMEN_PLUS_Y_REFERENT"] == [("lchy", "L+CH+Y", "LEITEN · ENTNEHMEN · DIES")],
        "all_readbacks_preserved": all(row["readback_preserved"] == "YES" for row in events),
        "empirical_three_families": {row["component_recipe"] for row in recipes if row["recipe_class"] == "EMPIRICAL_Y_CHY_ALLOGRAPH_FAMILY"} == {"Y", "OK+Y", "CHD+Y"},
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (recipes, events, chy, semantic, rules) for row in rows),
        "summary_pass": summary["status"] == "PASS" and (summary["open_y_events"], summary["terminal_chy_events"], summary["nonsemantic_terminal_chy"], summary["semantic_terminal_chy"]) == (122, 13, 12, 1),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
