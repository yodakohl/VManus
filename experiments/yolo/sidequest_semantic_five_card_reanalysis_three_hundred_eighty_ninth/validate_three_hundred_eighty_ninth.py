#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    decisions = read("THREE_HUNDRED_EIGHTY_NINTH_FIVE_CARD_DECISIONS.tsv")
    revised = read("THREE_HUNDRED_EIGHTY_NINTH_REVISED_14_LAYERED_READINGS.tsv")
    boundaries = read("THREE_HUNDRED_EIGHTY_NINTH_THREE_WHOLE_CARD_BOUNDARIES.tsv")
    checks = {
        "five_decisions": len(decisions) == 5,
        "two_promoted": Counter(row["new_route"] for row in decisions)["COMPONENT_DIRECT"] == 2,
        "three_whole": Counter(row["new_route"] for row in decisions)["WHOLE_CARD_MEMORY"] == 3,
        "fourteen_revised": len(revised) == 14,
        "eleven_components": Counter(row["read_route"] for row in revised)["COMPONENT_DIRECT"] == 11,
        "three_page_wholes": Counter(row["read_route"] for row in revised)["WHOLE_CARD_MEMORY"] == 3,
        "lcheey_corrected": next(row for row in revised if row["joint_tuple_id"] == "5fca8fc3dee57e1d8c1f")["atomic_reading_de"] == "benetzte Stelle",
        "three_boundaries": len(boundaries) == 3,
        "split_rejected": next(row for row in boundaries if row["tempting_split"] == "L+CHEEY")["decision"] == "REJECT_SPLIT_KEEP_LCHEEY_WHOLE",
        "positions_complete": {int(row["source_position"]) for row in revised} == set(range(1, 15)),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_NINTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
