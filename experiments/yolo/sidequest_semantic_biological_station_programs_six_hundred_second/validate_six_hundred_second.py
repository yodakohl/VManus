#!/usr/bin/env python3
"""Validate the six Biological station programs."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    programs = read("SIX_HUNDRED_SECOND_SIX_BIOLOGICAL_PROGRAMS.tsv")
    stations = read("SIX_HUNDRED_SECOND_SIXTEEN_STATION_INPUTS.tsv")
    steps = read("SIX_HUNDRED_SECOND_NINETY_SEVEN_STATION_STEPS.tsv")
    checks = {
        "six_records": len(programs) == 6 and {row["record"] for row in programs} == {f"B{i}" for i in range(1, 7)},
        "sixteen_stations": len(stations) == 16 and len({row["station_id"] for row in stations}) == 16,
        "ninety_seven_statements": len(steps) == 97 and len({row["statement_id"] for row in steps}) == 97,
        "two_hundred_eighty_one_events": sum(int(row["event_count"]) for row in steps) == 281,
        "all_events_unique": len({event for row in steps for event in row["event_ids"].split("|")}) == 281,
        "all_stations_used": {row["station_id"] for row in stations} == {row["owner_id"] for row in steps},
        "all_primary_inputs_viable": all(row["primary_compatibility"] in {"DIRECT_WORKING_MATCH", "PLAUSIBLE_MATCH"} for row in stations),
        "all_steps_concrete": all(row["primary_product_de"] and row["selected_concrete_step_de"] and row["surface_sequence"] for row in steps),
        "both_readings_present": all(row["therapeutic_reading_de"] and row["bathhouse_reading_de"] for row in steps),
        "local_only": all(row["cross_station_transfer_claim"] == "NONE__LOCAL_OWNER_SEQUENCE_ONLY" for row in steps),
        "mixed_decision": {row["selected_reading"] for row in programs} == {"THERAPEUTIC_LEAD", "HYBRID_TIE", "TECHNICAL_LEAD"},
        "no_global_pipe": all(row["global_pipe_claim"] == "NONE__SEPARATE_LOCAL_STATIONS" for row in programs),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
