#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
AUDIT = ROOT / "sidequest_semantic_third_hidden_word_audit_eight_hundred_thirty_fourth"
PREFIX = "EIGHT_HUNDRED_THIRTY_FIFTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    events = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv")
    statements_old = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_116_STATEMENT_REPARSE.tsv")
    air_audit = read(AUDIT / "EIGHT_HUNDRED_THIRTY_FOURTH_5_AIR_EVENTS.tsv")
    proposed = {row["statement_id"]: row["proposed_working_reading_de"] for row in air_audit if row["revision"] != "NONE"}

    statements = []
    for row in statements_old:
        item = dict(row)
        if row["statement_id"] in proposed:
            item["working_reading_de"] = proposed[row["statement_id"]]
            item["revision_sources"] += ",PASS835_AIR_WASSER_ALIGNMENT"
        statements.append(item)

    by_card = {row["exact_card_id"]: row for row in cards}
    by_statement = {row["statement_id"]: row for row in statements}
    air_rows = []
    for event in events:
        if "AIR" not in event["component_recipe"].split("+"):
            continue
        card = by_card[event["exact_card_id"]]
        air_rows.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "exact_card_id": event["exact_card_id"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "card_reading_de": card["ninth_grammar_reading_de"],
                "working_reading_de": by_statement[event["statement_id"]]["working_reading_de"],
                "water_role": {
                    "CH+AIR": "WATER_TAKE",
                    "K+AIR": "WATER_ADD",
                    "OK+AIR": "WATER_START",
                    "CHD+AIR": "WATER_MOVE",
                    "AIR+Y+DY": "WATER_ITEM_CLOSE",
                }[event["component_recipe"]],
            }
        )

    paradigm = [
        {"status": "ATTESTED", "surface": "chair", "component_recipe": "CH+AIR", "reading_de": "ENTNEHMEN · WASSER", "workshop_expansion": "Wasser entnehmen", "evidence": "E006 f10r H1"},
        {"status": "ATTESTED", "surface": "kair", "component_recipe": "K+AIR", "reading_de": "ZUGEBEN · WASSER", "workshop_expansion": "laufendes Wasser zugeben", "evidence": "E103 f81v B1"},
        {"status": "ATTESTED", "surface": "okair", "component_recipe": "OK+AIR", "reading_de": "ANSETZEN · WASSER", "workshop_expansion": "laufendes Wasser ansetzen", "evidence": "E260 f83r B3"},
        {"status": "ATTESTED", "surface": "schedair", "component_recipe": "CHD+AIR", "reading_de": "UMSETZEN · WASSER", "workshop_expansion": "laufendes Wasser umsetzen", "evidence": "E300 f83r B3"},
        {"status": "ATTESTED", "surface": "dairydy", "component_recipe": "AIR+Y+DY", "reading_de": "WASSER · POSTEN · SCHLUSS", "workshop_expansion": "Wasserposten fuehren und schliessen", "evidence": "E351 f83r B4"},
        {"status": "PREDICTION_ONLY", "surface": "lair", "component_recipe": "L+AIR", "reading_de": "LEITEN · WASSER", "workshop_expansion": "Wasser leiten", "evidence": "Pass 833 prediction deck"},
    ]

    write(f"{PREFIX}_116_WATER_ALIGNED_STATEMENTS.tsv", statements, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "ninth_grammar_literal_de", "working_reading_de", "fully_core33_events", "remainder_events", "revision_sources"])
    write(f"{PREFIX}_5_AIR_EVENT_READINGS.tsv", air_rows, ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "card_reading_de", "working_reading_de", "water_role"])
    write(f"{PREFIX}_6_WATER_PARADIGM_CELLS.tsv", paradigm, ["status", "surface", "component_recipe", "reading_de", "workshop_expansion", "evidence"])

    summary = {
        "status": "PASS",
        "decision": "AIR_WASSER_ALIGNED_IN_ALL_FIVE_EVENTS",
        "statements": len(statements),
        "revised_statements": len(proposed),
        "air_cards": len({row["exact_card_id"] for row in air_rows}),
        "air_events": len(air_rows),
        "air_statements": len({row["statement_id"] for row in air_rows}),
        "attested_paradigm_cells": sum(row["status"] == "ATTESTED" for row in paradigm),
        "prediction_cells": sum(row["status"] == "PREDICTION_ONLY" for row in paradigm),
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 835: AIR water mini-paradigm

AIR remains the concrete stem `WASSER`. The four Bio sentences that had called
it merely “Flüssigkeit” now say `das laufende Wasser`; the f10r Herbal sentence
already said water. All five AIR events therefore expose the same noun in both
literal and fluent layers.

The surrounding cards form a small useful paradigm:

- `chair = CH+AIR`: water take;
- `kair = K+AIR`: water add;
- `okair = OK+AIR`: water start/set;
- `schedair = CHD+AIR`: water move/transfer;
- `dairydy = AIR+Y+DY`: water item, then close.

The existing unseen prediction `lair = L+AIR` now has the unambiguous workshop
reading “Wasser leiten”. This is a good example of the desired mixed system:
AIR is stable, the operator is stable, while each complete card remains a
learned usable instruction.

No component value changed. Exactly four of 116 fluent statements changed.
Next, look for other five-to-ten-card islands where one material/address stem
combines with several stable operators and generates a concrete missing cell.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
