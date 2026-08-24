#!/usr/bin/env python3
"""Validate the complete 39-entry historical-layer dictionary."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_seventy_ninth.py")], check=True)
    roots = read("SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")
    trays = read("SIX_HUNDRED_SEVENTY_NINTH_8_APPRENTICE_TRAYS.tsv")
    cards = read("SIX_HUNDRED_SEVENTY_NINTH_173_COMPACT_CARD_TABLET.tsv")
    events = read("SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    root_set = {row["component"] for row in roots}
    checks = {
        "thirty_nine_roots": len(roots) == 39 and len(root_set) == 39,
        "eight_layers": len({row["historical_layer"] for row in roots}) == 8,
        "eight_trays": len(trays) == 8 and sum(int(row["entries"]) for row in trays) == 39,
        "tray_counts_match": Counter(row["historical_layer"] for row in roots) == Counter({row["historical_layer"]: int(row["entries"]) for row in trays}),
        "ten_simplified_values": sum(row["changed_for_teaching"] == "YES" for row in roots) == 10,
        "all_values_atomic": all(row["compact_table_value_de"] and " " not in row["compact_table_value_de"] for row in roots),
        "one_hundred_seventy_three_cards": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "all_card_components_known": all(set(row["component_recipe"].split("+")) <= root_set for row in cards),
        "three_hundred_eighty_one_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "all_events_bound_to_cards": all(row["card_no"] in {card["card_no"] for card in cards} for row in events),
        "no_empty_compact_readings": all(row["compact_atomic_reading_de"] for row in cards + events),
        "fixed_prose_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_SEVENTY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
