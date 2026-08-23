#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    decisions = read("TWO_HUNDRED_EIGHTY_SEVENTH_20_ALLOGRAPH_DECISIONS.tsv")
    recipes = read("TWO_HUNDRED_EIGHTY_SEVENTH_147_RESOLVED_RECIPES.tsv")
    occurrences = read("TWO_HUNDRED_EIGHTY_SEVENTH_126_OCCURRENCE_CHOICES.tsv")
    checks = {
        "decisions_20": len(decisions) == 20,
        "semantic_subtypes_18": sum(r["decision"] == "SEMANTIC_SUBTYPE_RESOLVED" for r in decisions) == 18,
        "local_allographs_2": sum(r["decision"] == "LOCAL_ALLOGRAPH_REMAINS" for r in decisions) == 2,
        "recipes_147": len(recipes) == 147,
        "recipe_card_types_149": sum(int(r["card_type_count"]) for r in recipes) == 149,
        "single_form_145": sum(int(r["card_type_count"]) == 1 for r in recipes) == 145,
        "ambiguous_2": sum(int(r["card_type_count"]) > 1 for r in recipes) == 2,
        "composed_events_352": sum(int(r["event_support"]) for r in recipes) == 352,
        "canonical_hits_350": sum(int(r["canonical_event_hits"]) for r in recipes) == 350,
        "occurrences_126": len(occurrences) == 126,
        "occurrence_events_unique": len({r["event_id"] for r in occurrences}) == 126,
        "all_values_present": all(r["resolved_value_de"].strip() for r in occurrences),
        "no_sealed_page": all("f84" not in "\t".join(r.values()).lower() for r in decisions + recipes + occurrences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
