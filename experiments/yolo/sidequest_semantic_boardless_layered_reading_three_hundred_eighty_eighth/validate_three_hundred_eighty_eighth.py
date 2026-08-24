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
    readings = read("THREE_HUNDRED_EIGHTY_EIGHTH_14_LAYERED_READINGS.tsv")
    layers = read("THREE_HUNDRED_EIGHTY_EIGHTH_FOUR_READING_LAYERS.tsv")
    checks = {
        "fourteen_cards": len(readings) == 14,
        "nine_components": Counter(row["read_route"] for row in readings)["COMPONENT_DIRECT"] == 9,
        "five_whole_cards": Counter(row["read_route"] for row in readings)["WHOLE_CARD_MEMORY"] == 5,
        "fourteen_picture_arguments": sum(row["picture_argument_required"] == "YES" for row in readings) == 14,
        "two_owners": Counter(row["owner_code"] for row in readings) == {"H4": 7, "B3": 7},
        "four_layers": len(layers) == 4,
        "boardless": all(row["board_call_used"] == "NO" for row in readings),
        "no_card_claims_domain_noun": all(row["fluent_domain_noun_from_card"] == "NO" for row in readings),
        "positions_complete": {int(row["source_position"]) for row in readings} == set(range(1, 15)),
        "all_readings_nonempty": all(row["atomic_reading_de"] and row["owner_expanded_reading_de"] for row in readings),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
