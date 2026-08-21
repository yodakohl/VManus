#!/usr/bin/env python3
"""Propagate the selected six-card V18 revision through the full V17 ledger."""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
V17 = HERE.parent / "sidequest_theory_candidates_v17"

SELECTED = {
    "0275fbf14e07935b0a45": (
        "temper the working liquid and keep it lukewarm", ".68", "TEMPER_LUKEWARM"
    ),
    "de7321bface5628e35d6": (
        "let the spent liquid drain into the lower receiving vessel; end this instruction",
        ".71", "DRAIN_TO_LOWER_RECEIVER_CLOSE",
    ),
    "259b2b3b0bf859882e2c": (
        "wash the used vessel or channel through once; end this instruction",
        ".61", "APPARATUS_WASH_THROUGH_CLOSE",
    ),
    "28ffbc88b97772a75f1e": (
        "set the mixed liquid aside in a covered receiving vessel; end this instruction",
        ".60", "RESERVE_MIXED_LIQUID_CLOSE",
    ),
    "4d4559019a961b834aa1": (
        "from the same prepared batch", ".66", "SAME_PREPARED_BATCH_REFERENCE"
    ),
    "2cc054357a929df85f64": (
        "then take the following ingredient or plant part", ".65", "NEXT_DOSSIER_DETAIL"
    ),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, fields: list[str], data: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    deck = read(V17 / "V17_SELECTED_RECURRENT_DECK.tsv")
    assert set(SELECTED) <= {row["exact_tuple_id"] for row in deck}
    for row in deck:
        key = row["exact_tuple_id"]
        if key in SELECTED:
            meaning, confidence, source_class = SELECTED[key]
            row["v17_selected_default"] = meaning
            row["confidence"] = confidence
            row["source_class"] = source_class
            row["selection_rule"] = "V18 six-card process reconstruction consensus"
    write(HERE / "V18_SELECTED_RECURRENT_DECK.tsv", list(deck[0]), deck)

    lexicon = read(V17 / "V17_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    changed_cards = 0
    for row in lexicon:
        key = row["lexicon_id"]
        if key in SELECTED and row["scope"] == "PROSE_EXACT_CARD":
            meaning, confidence, source_class = SELECTED[key]
            row["default_English"] = meaning
            row["confidence"] = confidence
            row["source_class"] = source_class
            row["inheritance_context_rule"] = (
                "V18 six-card full-process consensus; one concrete default across occurrences."
            )
            changed_cards += 1
    assert changed_cards == 6
    write(HERE / "V18_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv", list(lexicon[0]), lexicon)

    ledger = read(V17 / "V17_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    changed_events = 0
    for row in ledger:
        key = row["exact_tuple_id"]
        if key in SELECTED and row["ledger_scope"] == "GDT327_PROSE":
            meaning, confidence, source_class = SELECTED[key]
            row["default_English"] = meaning
            row["confidence"] = confidence
            row["source_class"] = source_class
            row["inheritance_context_rule"] = (
                "V18 full-process reconstruction; picture/rubric supplies omitted arguments."
            )
            changed_events += 1
    assert changed_events == 31
    assert len(ledger) == 776
    assert all(row["default_English"].strip() for row in ledger)
    assert not any(row["page"].startswith("f84") for row in ledger)
    write(HERE / "V18_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv", list(ledger[0]), ledger)
    print(f"changed_cards={changed_cards} changed_events={changed_events} total={len(ledger)}")


if __name__ == "__main__":
    main()
