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
    iin = read("FOUR_HUNDRED_EIGHTH_FOUR_IIN_OCCURRENCES.tsv")
    contrast = read("FOUR_HUNDRED_EIGHTH_AIIN_IIN_CONTRAST.tsv")
    rules = read("FOUR_HUNDRED_EIGHTH_FOUR_APPRENTICE_RULES.tsv")
    checks = {
        "four_iin_events": len(iin) == 4,
        "iin_event_ids": {row["event_id"] for row in iin} == {"E036", "E161", "E309", "E371"},
        "three_iin_cards": len({row["joint_tuple_id"] for row in iin}) == 3,
        "iin_contribution_constant": {row["iin_contribution"] for row in iin} == {"SOLLSTUFE_OR_SETTING"},
        "b5_second_opening_setting": next(row for row in iin if row["event_id"] == "E371")["selected_card_value_de"] == "ZWEITE_OEFFNUNGSSTELLUNG",
        "two_contrast_rows": len(contrast) == 2,
        "aiin_twenty_events": next(row for row in contrast if row["family"] == "AIIN")["events"] == "20",
        "iin_four_events": next(row for row in contrast if row["family"] == "IIN")["events"] == "4",
        "four_rules": len(rules) == 4,
        "aiin_noncomposition_rule": any(row["pattern"] == "AIIN" and "do not decompose" in row["learned_rule"] for row in rules),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_EIGHTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
