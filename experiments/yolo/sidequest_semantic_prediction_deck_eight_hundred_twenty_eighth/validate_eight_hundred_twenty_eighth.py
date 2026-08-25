#!/usr/bin/env python3
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
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_eighth.py")], check=True)
    audit = read("EIGHT_HUNDRED_TWENTY_EIGHTH_76_PREDICTION_AUDIT.tsv")
    recipes = read("EIGHT_HUNDRED_TWENTY_EIGHTH_68_RECIPE_DECISIONS.tsv")
    high_recipes = read("EIGHT_HUNDRED_TWENTY_EIGHTH_24_HIGH_VALUE_RECIPES.tsv")
    high_surfaces = read("EIGHT_HUNDRED_TWENTY_EIGHTH_30_HIGH_VALUE_SURFACES.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    surface_counts = Counter(row["component_recipe"] for row in high_surfaces)
    checks = {
        "complete_input": len(audit) == 76 and len(recipes) == 68,
        "compact_deck_counts": len(high_recipes) == 24 and len(high_surfaces) == 30,
        "ranks_exact": {int(row["recipe_rank"]) for row in high_recipes} == set(range(1, 25)),
        "recipe_surface_counts": all(surface_counts[row["component_recipe"]] == int(row["surface_candidates_n"]) for row in high_recipes),
        "all_unattested": all(row["attested_on_fixed_pages"] == "NO" for row in audit),
        "all_input_classified_once": all(row["selection_status"] for row in audit) and sum(row["selection_status"] == "HIGH_VALUE_DECK" for row in audit) == 30,
        "parked_counts": summary["parked_recipes"] == 44 and summary["parked_surfaces"] == 46,
        "no_dictionary_revision": summary["dictionary_revisions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
