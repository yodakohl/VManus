#!/usr/bin/env python3
"""Validate Pass 725 complete Herbal articles."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("SEVEN_HUNDRED_TWENTY_FIFTH_100_HERBAL_EVENTS.tsv")
    statements = read("SEVEN_HUNDRED_TWENTY_FIFTH_19_HERBAL_STATEMENTS.tsv")
    records = read("SEVEN_HUNDRED_TWENTY_FIFTH_5_COMPLETE_HERBAL_ARTICLES.tsv")
    water_statements = [row for row in statements if row["water_named"] == "YES"]
    forbidden = ("veilchen", "sonnentau", "rose", "knoblauch", "wein", "oel", "honig", "fieber", "husten", "wunde", "magen", "brust")
    all_text = " ".join(row["continuous_fluent_article_de"].lower() for row in records)
    checks = {
        "events_100_unique": len(events) == 100 and len({row["event_id"] for row in events}) == 100,
        "statements_19_unique": len(statements) == 19 and len({row["statement_id"] for row in statements}) == 19,
        "records_five": [row["record"] for row in records] == ["H1", "H2", "H3", "H4", "H5"],
        "event_counts_14_24_17_18_27": [int(row["events"]) for row in records] == [14, 24, 17, 18, 27],
        "water_only_h1s1": len(water_statements) == 1 and water_statements[0]["statement_id"] == "H1-S001",
        "one_herbal_air": sum("AIR" in row["component_recipe"].split("+") for row in events) == 1,
        "no_forbidden_specific_nouns": not any(word in all_text for word in forbidden),
        "no_declared_additions": all(row["added_named_species"] == row["added_disease"] == row["added_unanchored_ingredient"] == "NONE" for row in statements),
        "form_invariant": all(row["surface_owner_boundary_unchanged"] == "YES" for row in events),
        "all_fluent_nonempty": all(row["fluent_article_clause_de"] for row in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
