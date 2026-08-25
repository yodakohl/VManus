#!/usr/bin/env python3
"""Validate Pass 732 operation cross."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SEVEN_HUNDRED_THIRTY_SECOND_4_OPERATION_ROOTS.tsv")
    frames = read("SEVEN_HUNDRED_THIRTY_SECOND_7_ARGUMENT_FRAMES.tsv")
    cells = read("SEVEN_HUNDRED_THIRTY_SECOND_20_PARADIGM_CELLS.tsv")
    overlaps = read("SEVEN_HUNDRED_THIRTY_SECOND_3_MULTI_OPERATION_COMPOUNDS.tsv")
    ocards = read("SEVEN_HUNDRED_THIRTY_SECOND_74_OPERATION_CARDS.tsv")
    occurrences = read("SEVEN_HUNDRED_THIRTY_SECOND_157_OPERATION_OCCURRENCES.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_SECOND_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_SECOND_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_SECOND_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_SECOND_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["root"]: (row["short_value_de"], int(row["exact_cards"]), int(row["events"])) for row in roots}
    water = [row for row in cells if row["frame"] == "AIR"]
    checks = {
        "root_counts_exact": values == {"OK": ("ANSETZEN", 23, 79), "K": ("ZUGEBEN", 18, 21), "CH": ("ENTNEHMEN", 15, 16), "CHD": ("UMSETZEN", 22, 48)},
        "frames_seven_cells_twenty": len(frames) == 7 and len(cells) == 20,
        "water_complete": len(water) == 4 and {row["operation"] for row in water} == {"OK", "K", "CH", "CHD"} and sum(int(row["events"]) for row in water) == 4,
        "only_water_complete": [row["frame"] for row in frames if row["status"] == "COMPLETE_FOUR_OPERATION_PARADIGM"] == ["AIR"],
        "multi_operation_three": len(overlaps) == 3 and sum(int(row["events"]) for row in overlaps) == 7,
        "operation_cards_74": len(ocards) == 74 and len({row["exact_card_id"] for row in ocards}) == 74,
        "operation_occurrences_157": len(occurrences) == 157 and len({row["event_id"] for row in occurrences}) == 157,
        "complete_173_381_116_11": len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(records) == 11,
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
        "semantics_fixed": summary["semantic_changes"] == 0,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
