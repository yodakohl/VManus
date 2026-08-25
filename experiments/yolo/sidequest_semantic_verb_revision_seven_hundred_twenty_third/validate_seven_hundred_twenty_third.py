#!/usr/bin/env python3
"""Validate Pass 723 full T/CH/K revision."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_TWENTY_THIRD_39_REVISED_COMPONENTS.tsv")
    recipes = read("SEVEN_HUNDRED_TWENTY_THIRD_163_REVISED_RECIPES.tsv")
    cards = read("SEVEN_HUNDRED_TWENTY_THIRD_173_REVISED_CARDS.tsv")
    events = read("SEVEN_HUNDRED_TWENTY_THIRD_381_REVISED_EVENTS.tsv")
    statements = read("SEVEN_HUNDRED_TWENTY_THIRD_116_REVISED_STATEMENTS.tsv")
    records = read("SEVEN_HUNDRED_TWENTY_THIRD_11_REVISED_RECORDS.tsv")
    values = {row["component"]: row["revised_value_de"] for row in components}
    checks = {
        "counts_39_163_173_381_116_11": (len(components), len(recipes), len(cards), len(events), len(statements), len(records)) == (39, 163, 173, 381, 116, 11),
        "three_values": values["T"] == "ANWENDEN" and values["CH"] == "ENTNEHMEN" and values["K"] == "ZUGEBEN",
        "recipes_compositional": all(row["revised_reading_de"] == " · ".join(values[part] for part in row["component_recipe"].split("+")) for row in recipes),
        "cards_compositional": all(row["revised_reading_de"] == " · ".join(values[part] for part in row["component_recipe"].split("+")) for row in cards),
        "revision_counts_40_45_29_10": sum(row["semantic_revision"] == "YES" for row in recipes) == 40 and sum(row["semantic_revision"] == "YES" for row in events) == 45 and sum(row["semantic_revision"] == "YES" for row in statements) == 29 and sum(int(row["revised_statements"]) > 0 for row in records) == 10,
        "event_ids_unique": len({row["event_id"] for row in events}) == 381,
        "form_invariant": all(row["surface_unchanged"] == row["owner_unchanged"] == row["boundary_unchanged"] == "YES" for row in events),
        "statement_structure_invariant": all(row["surface_unchanged"] == row["owner_unchanged"] == row["statement_boundary_unchanged"] == row["line_relation_unchanged"] == "YES" for row in statements),
        "old_terms_removed_from_revised_records": all(row["old_terms_remaining_in_revision"] == "0" for row in records),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_THIRD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
