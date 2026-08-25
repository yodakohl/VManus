#!/usr/bin/env python3
"""Validate Pass 735 process verbs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SEVEN_HUNDRED_THIRTY_FIFTH_5_PROCESS_ROOTS.tsv")
    cells = read("SEVEN_HUNDRED_THIRTY_FIFTH_15_CANONICAL_PROCESS_CELLS.tsv")
    overlaps = read("SEVEN_HUNDRED_THIRTY_FIFTH_2_SH_CTH_OVERLAPS.tsv")
    pcards = read("SEVEN_HUNDRED_THIRTY_FIFTH_35_PROCESS_CARDS.tsv")
    occurrences = read("SEVEN_HUNDRED_THIRTY_FIFTH_63_PROCESS_OCCURRENCES.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_FIFTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_FIFTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_FIFTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_FIFTH_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["root"]: (row["short_value_de"], int(row["exact_cards"]), int(row["events"])) for row in roots}
    shey = [row for row in pcards if row["exact_card_id"] in {"PROC031", "PROC157"}]
    checks = {
        "root_counts_exact": values == {"CTH": ("BEREITEN", 8, 15), "SH": ("HALTEN", 20, 25), "SHED": ("ABSETZEN", 3, 15), "CHK": ("WAERMEN", 4, 7), "LSH": ("WASCHEN", 2, 3)},
        "cells_15_nonempty": len(cells) == 15 and all(int(row["events"]) > 0 for row in cells),
        "overlaps_two": len(overlaps) == 2 and all(row["decision"] == "SEQUENTIAL_COMPOSITION__SH_AND_CTH_REMAIN_DISTINCT" for row in overlaps),
        "process_cards_35": len(pcards) == 35 and len({row["exact_card_id"] for row in pcards}) == 35,
        "process_events_63": len(occurrences) == 63 and len({row["event_id"] for row in occurrences}) == 63,
        "shey_simple": len(shey) == 2 and all(row["component_recipe"] == "SH+EE+Y" and row["reading_de"] == "HALTEN · LANG · DIES" for row in shey),
        "complete_173_381_116_11": len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(records) == 11,
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
        "semantic_fixed": summary["semantic_changes"] == 0,
        "complex_shey_retired": summary["retired_complex_shey_gloss"] == "UNTIL_CLEAR_LIQUID_RUNS_OUT",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
