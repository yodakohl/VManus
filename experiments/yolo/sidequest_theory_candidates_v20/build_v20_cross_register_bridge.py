#!/usr/bin/env python3
"""Audit and propagate the 17 fixed Herbal/Bio bridge-card defaults."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
V19 = HERE.parent / "sidequest_theory_candidates_v19"
HERBAL = {"f10r", "f11r", "f55v", "f56r"}
BIO = {"f81v", "f82r", "f83r"}

REVISIONS = {
    "80ebbbbf238eee9f0aef": (
        "work it until evenly homogeneous", "PROCESS_CONDITION", ".52",
        "covers pounding a Herbal mass and joining a Bio preparation without changing the operation",
    ),
    "b5fcea1eaed06b2f2291": (
        "begin the next measured entry", "ENTRY_INSTRUCTION", ".58",
        "combines the recurrent entry-head behavior with the Herbal measured-portion use",
    ),
    "dd0ecaf5e27d81befffc": (
        "apply it at the place indicated by the drawing", "APPLICATION_LOCATION", ".55",
        "turns the common picture pointer into one executable Herbal/Bio instruction",
    ),
    "faf321940aed922846a9": (
        "take the final indicated share", "FINAL_SHARE_INSTRUCTION", ".42",
        "reconciles the final Herbal preparation with the marked Bio share",
    ),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    lexicon = read(V19 / "V19_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read(V19 / "V19_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    pages: dict[str, set[str]] = defaultdict(set)
    surfaces: dict[str, set[str]] = defaultdict(set)
    events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        if row["ledger_scope"] != "GDT327_PROSE":
            continue
        key = row["exact_tuple_id"]
        pages[key].add(row["page"])
        surfaces[key].add(row["surface"])
        events[key].append(row)
    bridges = sorted(key for key, seen in pages.items()
                     if seen & HERBAL and seen & BIO)
    assert len(bridges) == 17
    assert sum(len(events[key]) for key in bridges) == 136

    old_by_id = {row["lexicon_id"]: row for row in lexicon
                 if row["scope"] == "PROSE_EXACT_CARD"}
    audit = []
    for key in bridges:
        old = old_by_id[key]
        if key in REVISIONS:
            selected, source_class, confidence, reason = REVISIONS[key]
            disposition = "REVISED_CROSS_REGISTER_DEFAULT"
        else:
            selected = old["default_English"]
            source_class = old["source_class"]
            confidence = old["confidence"]
            reason = "existing concrete V18/V19 phrase remains executable in both registers"
            disposition = "PRESERVED"
        audit.append({
            "exact_tuple_id": key,
            "surface_realizations": "|".join(sorted(surfaces[key])),
            "events": str(len(events[key])),
            "herbal_events": str(sum(row["page"] in HERBAL for row in events[key])),
            "bio_events": str(sum(row["page"] in BIO for row in events[key])),
            "prior_default": old["default_English"],
            "selected_cross_register_default": selected,
            "source_class": source_class,
            "confidence": confidence,
            "disposition": disposition,
            "selection_reason": reason,
        })
    fields = list(audit[0])
    write(HERE / "V20_CROSS_REGISTER_CARD_AUDIT.tsv", fields, audit)

    occurrence_rows = []
    for key in bridges:
        selected = next(row["selected_cross_register_default"] for row in audit
                        if row["exact_tuple_id"] == key)
        for row in events[key]:
            occurrence_rows.append({
                "page": row["page"], "locus": row["locus"],
                "record": row["record"], "line": row["line"],
                "event_index": row["event_index"], "surface": row["surface"],
                "exact_tuple_id": key, "prior_default": row["default_English"],
                "selected_cross_register_default": selected,
                "register_side": "HERBAL" if row["page"] in HERBAL else "BIO",
            })
    write(HERE / "V20_136_OCCURRENCE_LEDGER.tsv", list(occurrence_rows[0]),
          occurrence_rows)

    changed_cards = 0
    for row in lexicon:
        key = row["lexicon_id"]
        if row["scope"] == "PROSE_EXACT_CARD" and key in REVISIONS:
            meaning, confidence, source_class, _ = REVISIONS[key]
            row["default_English"] = meaning
            row["confidence"] = confidence
            row["source_class"] = source_class
            row["inheritance_context_rule"] = (
                "V20 one concrete bridge instruction across Herbal and Biological registers."
            )
            changed_cards += 1
    assert changed_cards == 4
    write(HERE / "V20_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv", list(lexicon[0]), lexicon)

    changed_events = 0
    for row in ledger:
        key = row["exact_tuple_id"]
        if row["ledger_scope"] == "GDT327_PROSE" and key in REVISIONS:
            meaning, confidence, source_class, _ = REVISIONS[key]
            row["default_English"] = meaning
            row["confidence"] = confidence
            row["source_class"] = source_class
            row["inheritance_context_rule"] = (
                "V20 cross-register bridge default; picture/register supplies omitted arguments."
            )
            changed_events += 1
    assert changed_events == 23
    assert len(ledger) == 776
    write(HERE / "V20_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv", list(ledger[0]), ledger)
    print("PASS bridge_cards=17 occurrences=136 revised_cards=4 revised_events=23 total=776")


if __name__ == "__main__":
    main()
