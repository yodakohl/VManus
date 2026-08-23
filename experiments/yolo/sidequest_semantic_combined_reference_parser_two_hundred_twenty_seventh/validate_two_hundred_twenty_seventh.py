#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_TWENTY_SEVENTH_357_READING_UNITS.tsv", "TWO_HUNDRED_TWENTY_SEVENTH_ELEVEN_RECORD_SUMMARIES.tsv", "TWO_HUNDRED_TWENTY_SEVENTH_COMPOSITE_READING_MANUAL.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    units = read("TWO_HUNDRED_TWENTY_SEVENTH_357_READING_UNITS.tsv")
    records = read("TWO_HUNDRED_TWENTY_SEVENTH_ELEVEN_RECORD_SUMMARIES.tsv")
    manual = (OUT / "TWO_HUNDRED_TWENTY_SEVENTH_COMPOSITE_READING_MANUAL.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    event_ids = [event for row in units for event in row["source_event_ids"].split("|")]
    kinds = Counter(row["unit_kind"] for row in units)
    checks = {
        "357_units": len(units) == 357 and len({row["reading_unit_id"] for row in units}) == 357,
        "381_visible_events_exact_once": len(event_ids) == 381 and len(set(event_ids)) == 381 and set(event_ids) == {f"E{i:03d}" for i in range(1, 382)},
        "381_380_357": summary["visible_cards"] == 381 and summary["source_tokens"] == 380 and summary["reading_units"] == 357,
        "343_atomic_14_composite": summary["atomic_units"] == 343 and summary["composite_units"] == 14,
        "kind_inventory": kinds == {"ATOMIC_CARD": 343, "ABA_RETURN_FRAME": 8, "REPEATED_CLOSED_OPERATION": 3, "PAIR_PLUS_ABA_RETURN": 1, "OPEN_PAIR": 1, "CARRY_SINGLE_SOURCE": 1},
        "fifteen_rule_applications": summary["rule_applications"] == 15,
        "one_nested_unit": sum(row["unit_kind"] == "PAIR_PLUS_ABA_RETURN" and row["source_event_ids"] == "E020|E021|E022|E023" for row in units) == 1,
        "one_carry_source_token": sum(row["unit_kind"] == "CARRY_SINGLE_SOURCE" and row["source_token_count"] == "1" for row in units) == 1,
        "eleven_record_summaries": len(records) == 11 and sum(int(row["visible_cards"]) for row in records) == 381,
        "manual_states_three_levels": "381 sichtbare Karten" in manual and "380 Quelltoken" in manual and "357 Leseeinheiten" in manual,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in manual.lower() and not any("f84" in value.lower() for table in (units, records) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_seventh.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
