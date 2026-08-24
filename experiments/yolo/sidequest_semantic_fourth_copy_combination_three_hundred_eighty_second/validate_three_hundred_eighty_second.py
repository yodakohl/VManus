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
    source = read("THREE_HUNDRED_EIGHTY_SECOND_14_SOURCE_CARDS.tsv")
    visible = read("THREE_HUNDRED_EIGHTY_SECOND_15_VISIBLE_FORMS.tsv")
    calls = read("THREE_HUNDRED_EIGHTY_SECOND_14_RECONSTRUCTED_CALLS.tsv")
    checks = {
        "fourteen_sources": len(source) == 14,
        "fifteen_visible": len(visible) == 15,
        "fourteen_reconstructed": len(calls) == 14,
        "three_changes": sum(row["surface_changed"] == "YES" for row in source) == 3,
        "chosen_surfaces": {row["fourth_copy_surface"] for row in source if row["surface_changed"] == "YES"} == {"or", "dy", "daiin"},
        "all_registered": all(row["surface_registered"] == "YES" for row in source),
        "one_carry": Counter(row["visibility_role"] for row in visible)["MARKED_ANTICIPATION"] == 1,
        "fourteen_source_contributions": sum(int(row["source_contribution"]) for row in visible) == 14,
        "identities_exact": all(row["identity_match"] == "YES" for row in calls),
        "board_calls_exact": all(row["call_match"] == "YES" for row in calls),
        "owners": Counter(row["owner_code"] for row in source) == {"H4": 7, "B3": 7},
        "cycles": Counter(row["microcycle"] for row in source) == {"C1": 4, "C2": 3, "C3": 4, "C4": 3},
        "no_values_spoken": all(row["german_value_spoken_to_scribe"] == "NO" for row in source),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_SECOND_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
