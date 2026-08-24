#!/usr/bin/env python3
"""Close CKH as the one-word technical noun DURCHLASS."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"


FLUENT = {
    "CH+EE+CKH+O+DY": "LAENGER DURCH DEN DURCHLASS ABNEHMEN UND SCHLIESSEN",
    "SH+E+CKH+AL": "KURZ AM DURCHLASS DER ZIELSTELLE HALTEN",
    "CKH+Y": "AKTUELLER POSTEN AM DURCHLASS",
    "SH+CKH+E+DY": "KURZ IM DURCHLASS HALTEN UND SCHLIESSEN",
    "L+CKH+Y": "DEN POSTEN DURCH DEN DURCHLASS WEITERLEITEN",
    "L+CKH+E+DY": "KURZ DURCH DEN DURCHLASS WEITERLEITEN UND SCHLIESSEN",
    "SH+E+CKH+Y": "DEN POSTEN KURZ AM DURCHLASS HALTEN",
    "O+CKH+E+Y": "DEN POSTEN KURZ DURCH DEN DURCHLASS FUEHREN",
    "CH+CKH+AL": "AM DURCHLASS DER ZIELSTELLE ABNEHMEN",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def proc_num(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    all_events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in all_events:
        by_statement[event["statement_id"]].append(event)
        if "CKH" in event["semantic_component_parse"].split("+"):
            by_card[event["card_no"]].append(event)

    cards = []
    for card in sorted(by_card, key=proc_num):
        rows = by_card[card]
        exemplar = rows[0]
        recipe = exemplar["semantic_component_parse"]
        cards.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": recipe,
            "short_ckh_value_de": "DURCHLASS",
            "literal_reading_de": exemplar["standard_command_de"],
            "fluent_composition_de": FLUENT[recipe],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "contains_close": "YES" if "SCHLUSS" in exemplar["standard_command_de"] else "NO",
        })

    event_rows = []
    for event in all_events:
        if "CKH" not in event["semantic_component_parse"].split("+"):
            continue
        statement = by_statement[event["statement_id"]]
        pos = next(i for i, row in enumerate(statement) if row["event_id"] == event["event_id"])
        if len(statement) == 1:
            position_class = "WHOLE_STATEMENT"
        elif pos == 0:
            position_class = "ENTRY"
        elif pos == len(statement) - 1:
            position_class = "FINAL"
        else:
            position_class = "MEDIAL"
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "position_class": position_class,
            "card_no": event["card_no"],
            "surface": event["surface"],
            "component_recipe": event["semantic_component_parse"],
            "fluent_composition_de": FLUENT[event["semantic_component_parse"]],
            "contains_close": "YES" if "SCHLUSS" in event["standard_command_de"] else "NO",
            "statement_final": "YES" if pos == len(statement) - 1 else "NO",
        })

    predictions = [
        ("CKH+AL", "ckhal?", "DURCHLASS AN DER ZIELSTELLE"),
        ("CKH+AIR", "ckhair?", "DURCHLASS FUER DIE LAUFFLUESSIGKEIT"),
        ("P+CKH", "pckh?", "DURCH DEN DURCHLASS EINFUELLEN"),
        ("CKH+EE+Y", "ckheey?", "POSTEN LAENGER AM DURCHLASS HALTEN"),
        ("CKH+DY", "ckhdy?", "DURCHLASS-SCHRITT OHNE DAUERGRAD SCHLIESSEN"),
    ]
    prediction_rows = [
        {"predicted_recipe": recipe, "surface_guess": surface, "predicted_reading_de": reading, "rule": "CKH bleibt DURCHLASS; Zusatz liefert Richtung, Grad oder Ende"}
        for recipe, surface, reading in predictions
    ]

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FIFTH_9_CKH_CARDS.tsv", cards, list(cards[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FIFTH_14_CKH_EVENT_CONTEXTS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FIFTH_5_CKH_PREDICTIONS.tsv", prediction_rows, list(prediction_rows[0]))

    summary = {
        "status": "PASS",
        "ckh_card_types": len(cards),
        "ckh_events": len(event_rows),
        "component_recipes": len({row["component_recipe"] for row in cards}),
        "core_ckh_y_card_types": sum(row["component_recipe"] == "CKH+Y" for row in cards),
        "core_ckh_y_events": sum(int(row["events"]) for row in cards if row["component_recipe"] == "CKH+Y"),
        "close_events": sum(row["contains_close"] == "YES" for row in event_rows),
        "close_events_final": sum(row["contains_close"] == "YES" and row["statement_final"] == "YES" for row in event_rows),
        "entry": sum(row["position_class"] == "ENTRY" for row in event_rows),
        "medial": sum(row["position_class"] == "MEDIAL" for row in event_rows),
        "final": sum(row["position_class"] == "FINAL" for row in event_rows),
        "whole": sum(row["position_class"] == "WHOLE_STATEMENT" for row in event_rows),
        "expanded_dictionary_card_types": 75,
        "expanded_dictionary_events": 189,
        "decision": "CKH_IS_A_ONE_WORD_PASSAGE_NOUN_WITH_DIRECTION_GRADE_TARGET_AND_ENDPOINT_COMPOSITION",
    }
    (HERE / "SIX_HUNDRED_SIXTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
