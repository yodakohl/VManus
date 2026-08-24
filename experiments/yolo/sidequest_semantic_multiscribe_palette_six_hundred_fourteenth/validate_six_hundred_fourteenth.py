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
    rules = read("SIX_HUNDRED_FOURTEENTH_10_COMMAND_CARD_RULES.tsv")
    palette = read("SIX_HUNDRED_FOURTEENTH_20_CARD_SURFACE_PALETTE.tsv")
    replay = read("SIX_HUNDRED_FOURTEENTH_71_EVENT_SURFACE_REPLAY.tsv")
    checks = {
        "rules10": len(rules) == 10 and len({row["rule_id"] for row in rules}) == 10,
        "twenty_cards": len(palette) == 20 and len({row["card_no"] for row in palette}) == 20,
        "thirty_five_surfaces": sum(len(row["licensed_surfaces"].split("|")) for row in palette) == 35,
        "events71": len(replay) == 71 and len({row["event_id"] for row in replay}) == 71,
        "card_selection71": all(row["card_selection_correct"] == "YES" for row in replay),
        "licensed_surface71": all(row["surface_is_licensed"] == "YES" for row in replay),
        "three_desks": {row["desk"] for row in replay} == {"P_PREPARATION_DESK", "B_BATH_DESK", "S_STATION_DESK"},
        "no_semantic_surface_split": all("same command" in row["surface_teaching_rule_de"] for row in palette),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FOURTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
