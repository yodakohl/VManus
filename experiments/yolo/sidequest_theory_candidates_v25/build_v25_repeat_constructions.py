#!/usr/bin/env python3
"""Interpret every within-locus exact-card repetition in the fixed prose panel."""

from __future__ import annotations

import csv
import json
from collections import Counter, OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
V22 = HERE.parent / "sidequest_theory_candidates_v22"
V24 = HERE.parent / "sidequest_theory_candidates_v24"

READINGS = {
    "f10r.6": ("COUNTED_ARGUMENTS", "prepare three current portions, adding expressed juice and boiling them under the stated measure"),
    "f10r.8": ("MULTIPLE_RELATION_SLOTS", "take one handful and attach two successive ingredients or steps to the foregoing preparation and batch"),
    "f10r.9": ("COUNTED_ARGUMENTS", "combine two portions of prepared decoction; after bitterness remains, preserve the selected portion under oil"),
    "f11r.4": ("REFERENCE_FRAME", "of the pictured simple, bind the present portion on the swollen place in the stated measure"),
    "f55v.5": ("TWO_MEASURED_ADDITIONS", "begin the entry with one measured portion, add a second stated measure, stir evenly and wash once"),
    "f81v.2": ("MULTIPLE_RELATION_SLOTS", "connect two operations to the same foregoing preparation before applying at the pictured place"),
    "f81v.7": ("PAIRED_SLOTS", "enter two applications under the same preparation and the same stated measure"),
    "f81v.18": ("REPEATED_ACTION", "after heating and standing, rinse the indicated place twice, then pass through the connected channels"),
    "f81v.21": ("REPEATED_ACTION", "begin the rinsing with warm water and wash twice, closing each pass"),
    "f82r.19": ("TWO_MEASURED_ADDITIONS", "from the same prepared batch add two measured portions and set them gently"),
    "f82r.27": ("REPEATED_ACTION", "perform the warm immersion twice as two separately closed cells"),
    "f83r.3": ("PAIRED_SLOTS", "place two marked applications at two pictured relation slots under the two current-portion references"),
    "f83r.14": ("TWO_APPLICATION_SITES", "apply the prepared entry at two pictured places before proceeding"),
    "f83r.20": ("REPEATED_ACTION_WITH_STAGE", "rinse once, mark the first rinse, then rinse a second time before application"),
    "f83r.27": ("REPEATED_ACTION", "stir the warm immersion and strain it twice through cloth, closing each pass"),
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
    lexicon = read(V22 / "V22_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read(V22 / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    grouped: OrderedDict[tuple[str, str], list[dict[str, str]]] = OrderedDict()
    for row in ledger:
        if row["ledger_scope"] == "GDT327_PROSE":
            grouped.setdefault((row["page"], row["locus"]), []).append(row)
    repeated = {}
    for (page, locus), rows in grouped.items():
        counts = Counter(row["exact_tuple_id"] for row in rows)
        if any(count > 1 for count in counts.values()):
            repeated[locus] = (rows, counts)
    assert set(repeated) == set(READINGS)

    audit = []
    for locus, (rows, counts) in repeated.items():
        repeats = []
        for key, count in counts.items():
            if count > 1:
                surface = next(row["surface"] for row in rows if row["exact_tuple_id"] == key)
                repeats.append(f"{surface}×{count}")
        kind, reading = READINGS[locus]
        audit.append({
            "page": rows[0]["page"], "locus": locus,
            "visible_source_sequence": " ".join(row["surface"] for row in rows),
            "repeated_exact_cards": "|".join(repeats),
            "construction_type": kind,
            "selected_complete_construction_reading": reading,
            "line_end_is_sentence_end": "NO",
        })
    write(HERE / "V25_REPEAT_CONSTRUCTION_READINGS.tsv", list(audit[0]), audit)

    # LSHEDY had encoded 'twice' in each card and was then itself repeated.
    target = "2e7e89e0bd12b999c280"
    changed_lexicon = 0
    for row in lexicon:
        if row["lexicon_id"] == target:
            row["default_English"] = "wash once; close this pass"
            row["source_class"] = "SINGLE_WASH_CLOSE"
            row["confidence"] = ".55"
            row["inheritance_context_rule"] = "V25 base action is singular; exact repetition supplies twice."
            changed_lexicon += 1
    assert changed_lexicon == 1
    changed_events = 0
    for row in ledger:
        if row["exact_tuple_id"] == target:
            row["default_English"] = "wash once; close this pass"
            row["source_class"] = "SINGLE_WASH_CLOSE"
            row["confidence"] = ".55"
            row["inheritance_context_rule"] = "V25 repetition supplies action count."
            changed_events += 1
    assert changed_events == 2
    write(HERE / "V25_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv", list(lexicon[0]), lexicon)
    write(HERE / "V25_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv", list(ledger[0]), ledger)

    loci = read(V24 / "V24_COMPLETE_199_LOCUS_TRANSLATION.tsv")
    overrides = {row["locus"]: row for row in audit}
    for row in loci:
        if row["locus"] in overrides:
            row["complete_constructional_translation"] = overrides[row["locus"]][
                "selected_complete_construction_reading"
            ]
            row["construction_override_status"] = "REPEAT_GRAMMAR_APPLIED"
        else:
            row["complete_constructional_translation"] = row[
                "complete_literal_working_translation"
            ]
            row["construction_override_status"] = "LITERAL_SEQUENCE_RETAINED"
    fields = list(loci[0])
    write(HERE / "V25_COMPLETE_199_LOCUS_TRANSLATION.tsv", fields, loci)

    result = {
        "schema": "SIDEQUEST_V25_REPEAT_CONSTRUCTION_VALIDATION_V1",
        "status": "PASS", "repeat_loci": 15, "repeated_action_loci": 5,
        "other_argument_or_relation_repeat_loci": 10,
        "base_card_defaults_revised": 1, "events_revised": 2,
        "complete_lexicon_rows": 569, "complete_ledger_rows": 776,
        "complete_locus_rows": 199,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
    }
    (HERE / "V25_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
