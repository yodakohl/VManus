#!/usr/bin/env python3
"""Validate Pass 726 Biological local station protocols."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("SEVEN_HUNDRED_TWENTY_SIXTH_281_BIO_EVENTS.tsv")
    statements = read("SEVEN_HUNDRED_TWENTY_SIXTH_97_BIO_STATEMENTS.tsv")
    records = read("SEVEN_HUNDRED_TWENTY_SIXTH_6_BIO_RECORDS.tsv")
    resets = read("SEVEN_HUNDRED_TWENTY_SIXTH_10_OWNER_RESETS.tsv")
    air = read("SEVEN_HUNDRED_TWENTY_SIXTH_4_LOCAL_WATER_EVENTS.tsv")
    water_statements = [row for row in statements if row["water_named"] == "YES"]
    all_fluent = " ".join(row["fluent_local_station_clause_de"] for row in statements)
    checks = {
        "events_281_unique": len(events) == 281 and len({row["event_id"] for row in events}) == 281,
        "statements_97_unique": len(statements) == 97 and len({row["statement_id"] for row in statements}) == 97,
        "records_six": [row["record"] for row in records] == ["B1", "B2", "B3", "B4", "B5", "B6"],
        "statement_counts_21_22_34_16_3_1": [int(row["statements"]) for row in records] == [21, 22, 34, 16, 3, 1],
        "event_counts_66_62_86_47_11_9": [int(row["events"]) for row in records] == [66, 62, 86, 47, 11, 9],
        "resets_6_plus_4": len(resets) == 10 and sum(row["reset_kind"] == "BETWEEN_STATEMENTS" for row in resets) == 6 and sum(row["reset_kind"] == "INSIDE_STATEMENT" for row in resets) == 4,
        "air_four_exact": len(air) == 4 and {row["event_id"] for row in air} == {"E103", "E260", "E300", "E351"},
        "water_only_air_statements": {row["statement_id"] for row in water_statements} == {row["statement_id"] for row in air},
        "all_flow_local": all(row["global_flow_claim"] == "NONE" for row in events + statements + records + resets + air),
        "no_global_circuit_phrase": "Kreislauf" not in all_fluent and "kreislauf" not in all_fluent,
        "form_invariant": all(row["surface_owner_boundary_unchanged"] == "YES" for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
