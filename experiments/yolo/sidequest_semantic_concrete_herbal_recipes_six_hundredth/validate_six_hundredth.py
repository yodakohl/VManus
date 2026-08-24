#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    recipes = read("SIX_HUNDREDTH_FIVE_CONCRETE_HERBAL_RECIPES.tsv")
    steps = read("SIX_HUNDREDTH_NINETEEN_RECIPE_STEPS.tsv")
    events = read("SIX_HUNDREDTH_ONE_HUNDRED_HERBAL_EVENT_ROLES.tsv")
    rivals = read("SIX_HUNDREDTH_FIVE_RECIPE_RIVALS.tsv")
    checks = {
        "recipes5": len(recipes) == 5 and {row["record"] for row in recipes} == {f"H{i}" for i in range(1, 6)},
        "steps19": len(steps) == 19 and len({row["statement_id"] for row in steps}) == 19,
        "events100": len(events) == 100 and len({row["event_id"] for row in events}) == 100,
        "recipe_counts": sum(int(row["statements"]) for row in recipes) == 19 and sum(int(row["events"]) for row in recipes) == 100,
        "steps_bound": all(row["all_source_objects_preserved"] == "YES" and row["concrete_recipe_step_de"] for row in steps),
        "event_roles_complete": all(row["recipe_object_de"] and row["operation_de"] and row["local_output_de"] for row in events),
        "media_not_words": all(row["water_wine_oil_word_claim"] == "NONE__MEDIUM_IS_ARTICLE_CONTEXT" for row in events),
        "rivals5": len(rivals) == 5 and len({row["record"] for row in rivals}) == 5,
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDREDTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
