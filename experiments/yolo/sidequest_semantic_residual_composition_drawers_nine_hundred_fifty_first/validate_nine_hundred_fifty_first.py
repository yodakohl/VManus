#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fifty_first.py")], check=True)
    recipes = rows("PASS951_RESIDUAL_RECIPE_DRAWERS.tsv")
    events = rows("PASS951_903_RESIDUAL_EVENTS.tsv")
    recipe_map = {row["component_recipe"]: row for row in recipes}
    checks = [
        ("events_903", len(events) == 903, len(events)),
        ("events_unique", len({row["event_id"] for row in events}) == 903, "unique"),
        ("recipes_unique", len(recipe_map) == len(recipes), len(recipes)),
        ("all_recipes_bound", all(row["component_recipe"] in recipe_map for row in events), "bound"),
        ("single_is_basic", all(row["residual_drawer"] == "BASIC_ABBREVIATION" for row in recipes if int(row["component_count"]) == 1), "basic"),
        ("candidate_multicomponent", all(int(row["component_count"]) > 1 and int(row["events"]) >= 3 and int(row["page_count"]) >= 2 for row in recipes if row["residual_drawer"] == "NEXT_FORMULA_CANDIDATE"), "candidate"),
        ("all_values", all(row["current_short_reading_de"].strip() for row in recipes), "values"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in events).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS951_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
