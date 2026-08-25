#!/usr/bin/env python3
"""Validate Pass 733 grade and endpoint grammar."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SEVEN_HUNDRED_THIRTY_THIRD_5_STATE_ENDPOINT_ROOTS.tsv")
    pure = read("SEVEN_HUNDRED_THIRTY_THIRD_6_PURE_OK_GRADE_CELLS.tsv")
    cells = read("SEVEN_HUNDRED_THIRTY_THIRD_26_OPERATION_STATE_CELLS.tsv")
    firewall = read("SEVEN_HUNDRED_THIRTY_THIRD_105_DY_SURFACE_FIREWALL.tsv")
    scards = read("SEVEN_HUNDRED_THIRTY_THIRD_108_STATE_ENDPOINT_CARDS.tsv")
    occurrences = read("SEVEN_HUNDRED_THIRTY_THIRD_224_STATE_ENDPOINT_OCCURRENCES.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_THIRD_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_THIRD_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_THIRD_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_THIRD_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["root"]: (row["short_value_de"], int(row["exact_cards"]), int(row["events"])) for row in roots}
    false_rows = [row for row in firewall if row["contains_licensed_DY"] == "NO"]
    checks = {
        "root_counts_exact": values == {"E": ("KURZ", 34, 49), "EE": ("LANG", 17, 40), "EEE": ("VOLL", 2, 2), "Y": ("DIES", 60, 124), "DY": ("SCHLUSS", 37, 89)},
        "pure_ok_six_expected": len(pure) == 6 and all(int(row["events"]) == int(row["expected_events"]) for row in pure),
        "operation_cells_26": len(cells) == 26,
        "firewall_105_89_16": len(firewall) == 105 and sum(row["contains_licensed_DY"] == "YES" for row in firewall) == 89 and len(false_rows) == 16,
        "five_exact_dy_are_y": sum(row["surface"] == "dy" and row["component_recipe"] == "Y" for row in false_rows) == 5,
        "eleven_chdy_are_open": sum(row["component_recipe"] == "CHD+Y" for row in false_rows) == 11,
        "state_cards_108": len(scards) == 108 and len({row["exact_card_id"] for row in scards}) == 108,
        "state_events_224": len(occurrences) == 224 and len({row["event_id"] for row in occurrences}) == 224,
        "complete_173_381_116_11": len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(records) == 11,
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
        "semantics_fixed": summary["semantic_changes"] == 0,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
