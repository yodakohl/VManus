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
    tokens = read("THREE_HUNDRED_EIGHTY_FIFTH_11_TOKEN_COMPONENT_BACKREAD.tsv")
    tracks = read("THREE_HUNDRED_EIGHTY_FIFTH_THREE_GRADE_TRACKS.tsv")
    components = read("THREE_HUNDRED_EIGHTY_FIFTH_EIGHT_COMPONENT_MANUAL.tsv")
    checks = {
        "eleven_tokens": len(tokens) == 11,
        "three_tracks": len(tracks) == 3,
        "track_lengths": Counter(row["track"] for row in tokens) == {"KURZ": 4, "LÄNGER": 4, "VOLLSTÄNDIG": 3},
        "seven_cards": len({row["joint_tuple_id"] for row in tokens}) == 7,
        "eight_components": len(components) == 8,
        "all_existing": all(row["existing_registered_card"] == "YES" for row in tokens),
        "nothing_invented": all(row["new_surface_invented"] == "NO" for row in tokens),
        "two_open_closed_pairs": sum(row["open_to_closed_pair"] == "YES" for row in tracks) == 2,
        "top_gap_explicit": next(row for row in tracks if row["track"] == "VOLLSTÄNDIG")["open_to_closed_pair"] == "NO_OPEN_TOP_GRADE_CARD_REGISTERED",
        "backreads_nonempty": all(row["strict_component_backread_de"] and row["short_card_reading_de"] for row in tokens),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_FIFTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
