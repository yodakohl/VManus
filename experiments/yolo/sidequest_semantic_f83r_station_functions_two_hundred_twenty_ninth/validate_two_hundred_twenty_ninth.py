#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_TWENTY_NINTH_THREE_STATION_FUNCTIONS.tsv",
    "TWO_HUNDRED_TWENTY_NINTH_THIRTY_FIVE_OWNED_EVENTS.tsv",
    "TWO_HUNDRED_TWENTY_NINTH_SIXTEEN_STATION_STATEMENT_READINGS.tsv",
    "TWO_HUNDRED_TWENTY_NINTH_THREE_READABLE_STATIONS.md",
    "TWO_HUNDRED_TWENTY_NINTH_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    stations = read(ARTIFACTS[0])
    events = read(ARTIFACTS[1])
    statements = read(ARTIFACTS[2])
    readable = (OUT / ARTIFACTS[3]).read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    station_counts = {station: sum(row["station_id"] == station for row in events) for station in {row["station_id"] for row in events}}
    checks = {
        "three_stations": len(stations) == 3,
        "thirty_five_unique_events": len(events) == 35 and len({row["event_id"] for row in events}) == 35,
        "exact_station_counts": station_counts == {"F83_STATION_1": 10, "F83_STATION_2": 9, "F83_STATION_3": 16},
        "sixteen_statements": len(statements) == 16 and {row["statement_id"] for row in statements} == {f"B3-S{i:03d}" for i in range(1, 17)},
        "exact_event_bounds": {row["event_id"] for row in events} == {f"E{i:03d}" for i in range(229, 264)},
        "owner_break_respected": "E263" in {row["event_id"] for row in events} and "E264" not in {row["event_id"] for row in events},
        "b3s016_partial": next(row for row in statements if row["statement_id"] == "B3-S016")["owner_scope"] == "PARTIAL_BEFORE_OWNER_BREAK",
        "owners_match": all(row["visible_owner"] == next(station["visible_owner"] for station in stations if station["station_id"] == row["station_id"]) for row in events),
        "all_readings_concrete": all(row["station_reading_de"].strip() for row in statements),
        "no_global_flow_claim": "kein behaupteter geschlossener Wasserkreislauf" in readable,
        "summary_counts": summary["stations"] == 3 and summary["fields"] == 16 and summary["owned_events"] == 35 and summary["statements"] == 16,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_ninth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
