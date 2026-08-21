#!/usr/bin/env python3
"""Select V19 R2 locally while preserving V18 cross-register defaults."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
V18 = HERE.parent / "sidequest_theory_candidates_v18"
HERBAL = {"f10r", "f11r", "f55v", "f56r"}


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
    old_lexicon = read(V18 / "V18_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    old_ledger = read(V18 / "V18_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    r2_dictionary = read(HERE / "V19_R2_HERBAL_CARD_DICTIONARY.tsv")
    r2_events = read(HERE / "V19_R2_100_EVENT_INTERLINEAR.tsv")

    old_by_id = {
        row["lexicon_id"]: row for row in old_lexicon
        if row["scope"] == "PROSE_EXACT_CARD"
    }
    r2_by_id = {row["exact_tuple_id"]: row for row in r2_dictionary}
    pages: dict[str, set[str]] = defaultdict(set)
    for row in old_ledger:
        if row["ledger_scope"] == "GDT327_PROSE":
            pages[row["exact_tuple_id"]].add(row["page"])

    herbal_ids = {row["exact_tuple_id"] for row in r2_dictionary}
    assert len(herbal_ids) == 66
    herbal_only = {key for key in herbal_ids if pages[key] <= HERBAL}
    shared = herbal_ids - herbal_only
    assert len(herbal_only) == 49
    assert len(shared) == 17

    selected_dictionary = []
    for row in r2_dictionary:
        key = row["exact_tuple_id"]
        prior = old_by_id[key]
        selected = dict(row)
        selected["prior_v18_default"] = prior["default_English"]
        if key in herbal_only:
            selected["selected_default_phrase"] = row["concrete_default_phrase"]
            selected["selection_scope"] = "V19_HERBAL_ONLY_R2"
        else:
            selected["selected_default_phrase"] = prior["default_English"]
            selected["selection_scope"] = "V18_CROSS_REGISTER_PRESERVED"
        selected_dictionary.append(selected)
    dictionary_fields = list(r2_dictionary[0]) + [
        "prior_v18_default", "selected_default_phrase", "selection_scope"
    ]
    write(HERE / "V19_SELECTED_HERBAL_DICTIONARY.tsv", dictionary_fields,
          selected_dictionary)

    selected_events = []
    for row in r2_events:
        key = row["exact_tuple_id"]
        selected = dict(row)
        if key in herbal_only:
            selected["selection_scope"] = "V19_HERBAL_ONLY_R2"
        else:
            prior = old_by_id[key]
            selected["default_English"] = prior["default_English"]
            selected["source_class"] = prior["source_class"]
            selected["confidence"] = prior["confidence"]
            selected["inheritance_context_rule"] = (
                "V18 cross-register default preserved; V19 supplies Herbal context only."
            )
            selected["selection_scope"] = "V18_CROSS_REGISTER_PRESERVED"
        selected_events.append(selected)
    event_fields = list(r2_events[0]) + ["selection_scope"]
    write(HERE / "V19_SELECTED_100_EVENT_INTERLINEAR.tsv", event_fields,
          selected_events)

    lexicon = [dict(row) for row in old_lexicon]
    changed_cards = 0
    for row in lexicon:
        key = row["lexicon_id"]
        if row["scope"] == "PROSE_EXACT_CARD" and key in herbal_only:
            chosen = r2_by_id[key]
            row["default_English"] = chosen["concrete_default_phrase"]
            row["source_class"] = chosen["source_class"]
            row["confidence"] = chosen["confidence"]
            row["inheritance_context_rule"] = (
                "V19 selected four-page Herbal article reconstruction; picture supplies "
                "the omitted plant or part argument."
            )
            changed_cards += 1
    assert changed_cards == 49
    write(HERE / "V19_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv", list(lexicon[0]), lexicon)

    ledger = [dict(row) for row in old_ledger]
    changed_events = 0
    for row in ledger:
        key = row["exact_tuple_id"]
        if row["ledger_scope"] == "GDT327_PROSE" and key in herbal_only:
            chosen = r2_by_id[key]
            row["default_English"] = chosen["concrete_default_phrase"]
            row["source_class"] = chosen["source_class"]
            row["confidence"] = chosen["confidence"]
            row["inheritance_context_rule"] = (
                "V19 Herbal article reconstruction; pictured owner and prior clause "
                "supply omitted arguments; a physical line need not end the sentence."
            )
            changed_events += 1
    assert changed_events == 56
    assert len(ledger) == 776
    assert all(row["default_English"].strip() for row in ledger)
    assert not any(row["page"].startswith("f84") for row in ledger)
    write(HERE / "V19_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv", list(ledger[0]), ledger)

    print(
        "PASS herbal_types=66 herbal_only_types=49 shared_types=17 "
        "changed_events=56 total_ledger=776"
    )


if __name__ == "__main__":
    main()
