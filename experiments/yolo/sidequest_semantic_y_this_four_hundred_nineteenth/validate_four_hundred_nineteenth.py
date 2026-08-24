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
    naked = read("FOUR_HUNDRED_NINETEENTH_EIGHTEEN_NAKED_Y.tsv")
    wrappers = read("FOUR_HUNDRED_NINETEENTH_TWELVE_Y_WRAPPER_FAMILIES.tsv")
    b2 = read("FOUR_HUNDRED_NINETEENTH_B2_THREE_CARD_CELL.tsv")
    models = read("FOUR_HUNDRED_NINETEENTH_FOUR_Y_MODELS.tsv")
    checks = {
        "eighteen_naked_y": len(naked) == 18,
        "one_exact_base_card": len({row["joint_tuple_id"] for row in naked}) == 1,
        "six_renderer_surfaces": len({row["surface"] for row in naked}) == 6,
        "dies_invariant": {row["portable_value_de"] for row in naked} == {"dies"},
        "three_split_items": sum(row["referent_behavior"] == "ENUMERATES_ANONYMOUS_SPLIT_ITEMS" for row in naked) == 3,
        "b2_inherits_portion": [row for row in naked if row["event_id"] == "E170"][0]["referent_behavior"] == "INHERITS_JUST_ADDED_PORTION",
        "twelve_wrapper_families": len(wrappers) == 12,
        "productive_event_sum": sum(int(row["events"]) for row in wrappers) == 58,
        "three_b2_events": len(b2) == 3 and b2[1]["small_value_de"] == "dies",
        "four_models": len(models) == 4,
        "dies_selected": [row["candidate"] for row in models if row["decision"] == "SELECT_SHORTEST"] == ["DIES"],
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (naked, wrappers, b2, models) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_NINETEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
