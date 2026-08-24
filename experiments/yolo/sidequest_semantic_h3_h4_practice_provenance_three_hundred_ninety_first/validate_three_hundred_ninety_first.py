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
    provenance = read("THREE_HUNDRED_NINETY_FIRST_14_PRACTICE_CARD_PROVENANCE.tsv")
    genuine = read("THREE_HUNDRED_NINETY_FIRST_EIGHT_GENUINE_H3_H4_STATEMENTS.tsv")
    stages = read("THREE_HUNDRED_NINETY_FIRST_NINE_STAGE_ALIGNMENT.tsv")
    native = sum(row["practice_owner_native_card"] == "YES" for row in provenance)
    h4_native = sum(row["practice_owner"] == "H4" and row["practice_owner_native_card"] == "YES" for row in provenance)
    b3_native = sum(row["practice_owner"] == "B3" and row["practice_owner_native_card"] == "YES" for row in provenance)
    checks = {
        "fourteen_practice_cards": len(provenance) == 14,
        "native_plus_borrowed": native + sum(row["practice_owner_native_card"] == "NO" for row in provenance) == 14,
        "owner_native_split": native == 7 and h4_native == 2 and b3_native == 5,
        "eight_genuine_statements": len(genuine) == 8,
        "h3_h4_split": sum(row["record_unit_id"] == "H3" for row in genuine) == 4 and sum(row["record_unit_id"] == "H4" for row in genuine) == 4,
        "nine_stages": len(stages) == 9,
        "cphy_borrowing_explicit": "deliberate H3 borrowing" in next(row for row in stages if row["functional_stage"] == "SECOND_SEPARATION")["interpretation"],
        "practice_not_translation": all(row["claim_limit"] == "TEACHING_SYNTHESIS_NOT_H4_TRANSLATION" for row in provenance),
        "positions_complete": {int(row["source_position"]) for row in provenance} == set(range(1, 15)),
        "native_nonzero": native > 0,
        "borrowed_nonzero": native < 14,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks), "owner_native_cards": native, "h4_native_cards": h4_native, "b3_native_cards": b3_native}
    (HERE / "THREE_HUNDRED_NINETY_FIRST_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks; owner-native {native}/14 (H4 {h4_native}/7, B3 {b3_native}/7)")


if __name__ == "__main__":
    main()
