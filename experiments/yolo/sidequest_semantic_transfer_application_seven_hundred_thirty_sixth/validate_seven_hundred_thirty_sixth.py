#!/usr/bin/env python3
"""Validate Pass 736 transfer/application cross."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SEVEN_HUNDRED_THIRTY_SIXTH_4_TRANSFER_ROOTS.tsv")
    frames = read("SEVEN_HUNDRED_THIRTY_SIXTH_5_ARGUMENT_FRAMES.tsv")
    cells = read("SEVEN_HUNDRED_THIRTY_SIXTH_11_PARADIGM_CELLS.tsv")
    tcards = read("SEVEN_HUNDRED_THIRTY_SIXTH_36_TRANSFER_CARDS.tsv")
    occurrences = read("SEVEN_HUNDRED_THIRTY_SIXTH_46_TRANSFER_OCCURRENCES.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_SIXTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_SIXTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_SIXTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_SIXTH_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_SIXTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["root"]: (row["short_value_de"], int(row["exact_cards"]), int(row["events"])) for row in roots}
    checks = {
        "root_counts_exact": values == {"L": ("LEITEN", 18, 27), "P": ("FUELLEN", 3, 3), "R": ("KUEHLEN", 6, 6), "T": ("ANWENDEN", 9, 10)},
        "frames_five_cells_eleven": len(frames) == 5 and len(cells) == 11,
        "transfer_cards_36": len(tcards) == 36 and len({row["exact_card_id"] for row in tcards}) == 36,
        "transfer_occurrences_46": len(occurrences) == 46 and len({row["event_id"] for row in occurrences}) == 46,
        "no_root_overlap": all("+" not in row["transfer_roots"] for row in occurrences),
        "complete_173_381_116_11": len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(records) == 11,
        "event_card_readings_match": all(next(card["pass736_reading_de"] for card in cards if card["exact_card_id"] == row["card_no"]) == row["pass736_reading_de"] for row in events),
        "l_ol_is_lead_continue": next(row for row in cards if row["component_recipe"] == "L+OL")["pass736_reading_de"] == "LEITEN · WEITER",
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
