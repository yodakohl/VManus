#!/usr/bin/env python3
"""Validate Pass 721 compact apprentice release."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_TWENTY_FIRST_39_COMPONENT_SHEET.tsv")
    families = read("SEVEN_HUNDRED_TWENTY_FIRST_163_RECIPE_INDEX.tsv")
    cards = read("SEVEN_HUNDRED_TWENTY_FIRST_173_CARD_SURFACE_REGISTER.tsv")
    rules = read("SEVEN_HUNDRED_TWENTY_FIRST_16_OPERATIONAL_RULES.tsv")
    dockets = read("SEVEN_HUNDRED_TWENTY_FIRST_12_DOCKET_EXERCISE.tsv")
    replay = read("SEVEN_HUNDRED_TWENTY_FIRST_27_FORWARD_BACKWARD_REPLAY.tsv")
    surfaces = {surface for row in cards for surface in row["registered_surfaces"].split("|")}
    checks = {
        "inventory_39_163_173_230": len(components) == 39 and len(families) == 163 and len(cards) == 173 and len(surfaces) == 230,
        "rules_16": len(rules) == 16 and len({row["rule_id"] for row in rules}) == 16,
        "dockets_12": len(dockets) == 12 and len({row["docket_id"] for row in dockets}) == 12,
        "replay_27": len(replay) == 27 and len({row["master_event_id"] for row in replay}) == 27,
        "cards_roundtrip_27": all(row["card_roundtrip"] == "YES" for row in replay),
        "recipes_roundtrip_27": all(row["recipe_roundtrip"] == "YES" for row in replay),
        "structure_roundtrip_27": all(row["owner_roundtrip"] == row["line_roundtrip"] == row["statement_roundtrip"] == "YES" for row in replay),
        "all_card_families_known": {row["semantic_family"] for row in cards} <= {row["semantic_family"] for row in families},
        "sheet_present": (HERE / "SEVEN_HUNDRED_TWENTY_FIRST_APPRENTICE_SHEET.md").is_file(),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_FIRST_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
