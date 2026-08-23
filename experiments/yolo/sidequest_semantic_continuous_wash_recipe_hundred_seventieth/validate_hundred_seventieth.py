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
    events = read("HUNDRED_SEVENTIETH_53_EVENT_CONTINUOUS_RECIPE.tsv")
    clauses = read("HUNDRED_SEVENTIETH_17_CLAUSE_RECIPE.tsv")
    supplies = read("HUNDRED_SEVENTIETH_12_SILENT_SUPPLIES.tsv")
    supply_ids = {row["supply_id"] for row in supplies}
    used = {sid for row in clauses for sid in row["silent_supply_ids"].split("|")}
    checks = {
        "all_53_events": len(events) == 53,
        "combined_order_exact": [int(row["combined_order"]) for row in events] == list(range(1, 54)),
        "source_event_counts": sum(row["source_record"] == "H3" for row in events) == 17 and sum(row["source_record"] == "B4" for row in events) == 36,
        "all_17_clauses": len(clauses) == 17,
        "clause_partition": len({row["statement_id"] for row in clauses}) == 17 and {row["statement_id"] for row in events} == {row["statement_id"] for row in clauses},
        "all_12_supplies": len(supplies) == 12 and supply_ids == {f"A{i:02d}" for i in range(1, 13)},
        "all_supplies_used": used == supply_ids,
        "no_dictionary_changes": {row["dictionary_change"] for row in events} == {"NO"},
        "all_concrete": all(row["concrete_recipe_expansion_de"].strip() for row in events),
        "exact_clear_extract_bridge": sum(row["master_card_id"] == "MC119" for row in events) == 2,
        "sealed_pages_absent": all(row["page"] in {"f11r", "f83r"} for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
