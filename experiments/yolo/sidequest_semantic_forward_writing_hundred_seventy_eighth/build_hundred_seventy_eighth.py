#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


TOKENS = [
    (1, 1, "RESUME_PREVIOUS", "vom vorigen Posten", "MC142", "dchol"),
    (2, 1, "SELECT_CLEAR_EXTRACT", "Klarauszug waehlen", "MC119", "shey"),
    (3, 1, "SET_MEASURE", "auf Sollmass bringen", "MC039", "aiin"),
    (4, 2, "WARM_BRIEFLY", "kurz waermen", "MC147", "cheky"),
    (5, 2, "PLACE_INSERT", "Einlage einsetzen", "MC059", "dain"),
    (6, 2, "TRANSFER_CHARGE", "Charge ueberfuehren", "MC074", "chedy"),
    (7, 2, "HOLD_LONG_CLOSE", "lange einwirken und Feld schliessen", "MC082", "qokeedy"),
    (8, 3, "FIRST_PASS_CLOSE", "einmal durchlassen und Feld schliessen", "MC143", "shckhedy"),
    (9, 4, "SECOND_PASS_CLOSE", "zweites Mal durchlassen und Feld schliessen", "MC143", "shckhedy"),
    (10, 5, "SELECT_PORTION", "Anteil waehlen", "MC105", "kain"),
    (11, 5, "MOVE_TO_TARGET", "dorthin bringen", "MC154", "dal"),
    (12, 5, "SET_AT_TARGET", "an der Zielstelle einsetzen", "MC026", "qoky"),
    (13, 5, "WASH_CLOSE", "Waschgang ausfuehren und schliessen", "MC038", "lshedy"),
]


FIELDS = [
    (1, "dchol shey aiin", "vom vorigen Klarauszug ein Sollmass nehmen", "OPEN", "NEW_COMPOSITION"),
    (2, "cheky dain chedy qokeedy", "kurz waermen Einlage setzen Charge ueberfuehren lange einwirken", "CLOSED", "NEW_COMPOSITION"),
    (3, "shckhedy", "erster Durchgang", "CLOSED", "KNOWN_CADENCE_EXEMPLAR"),
    (4, "shckhedy", "zweiter Durchgang", "CLOSED", "KNOWN_CADENCE_EXEMPLAR"),
    (5, "kain dal qoky lshedy", "Anteil zur Zielstelle bringen einsetzen und waschen", "CLOSED", "NEW_COMPOSITION"),
]


AMBIGUITIES = [
    ("A1", "dchol", "welcher vorige Ansatz", "record- oder Meisterkontext"),
    ("A2", "aiin", "welche Einheit und Menge", "lokaler Sollwert im Exemplar"),
    ("A3", "dain", "Material und Form der Einlage", "sichtbare Station oder Werkzeugtafel"),
    ("A4", "shckhedy", "genauer Durchlass und Richtung", "lokale Apparatur; keine globale Richtung"),
    ("A5", "dal", "welche Zielstelle", "Bildbesitzer oder demonstrierter Koerperort"),
    ("A6", "qoky", "welcher konkrete Auftrag", "aktiver Posten und Ziel bestimmen die Expansion"),
    ("A7", "lshedy", "was und womit gewaschen wird", "Produkt- und Stationskontext"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = {row["master_card_id"]: row for row in read(DICTIONARY)}
    token_rows = []
    for order, field, step, source, card_id, surface in TOKENS:
        card = dictionary[card_id]
        token_rows.append(
            {
                "token_order": order,
                "field": field,
                "source_step": step,
                "source_instruction_de": source,
                "master_card_id": card_id,
                "chosen_visible_surface": surface,
                "dictionary_value_de": card["portable_card_value_de"],
                "surface_is_registered": "YES" if surface in card["registered_surfaces"].split("|") else "NO",
                "decoded_step_de": source,
            }
        )
    write(OUT / "HUNDRED_SEVENTY_EIGHTH_13_TOKEN_FORWARD_ENCODING.tsv", token_rows)

    field_rows = [
        {
            "field": field,
            "visible_card_sequence": visible,
            "strict_atomic_reading_de": reading,
            "field_status": close,
            "sequence_source": source,
        }
        for field, visible, reading, close, source in FIELDS
    ]
    write(OUT / "HUNDRED_SEVENTY_EIGHTH_5_FIELD_WRITING_EXERCISE.tsv", field_rows)

    ambiguity_rows = [
        {
            "ambiguity_id": aid,
            "surface_or_card": surface,
            "missing_information_de": missing,
            "workshop_resolution_de": resolution,
        }
        for aid, surface, missing, resolution in AMBIGUITIES
    ]
    write(OUT / "HUNDRED_SEVENTY_EIGHTH_7_ROUNDTRIP_AMBIGUITIES.tsv", ambiguity_rows)

    summary = {
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "source_steps": len(token_rows),
        "visible_tokens": len(token_rows),
        "distinct_cards": len({row["master_card_id"] for row in token_rows}),
        "fields": len(field_rows),
        "newly_composed_fields": sum(row["sequence_source"] == "NEW_COMPOSITION" for row in field_rows),
        "known_cadence_fields": sum(row["sequence_source"] == "KNOWN_CADENCE_EXEMPLAR" for row in field_rows),
        "roundtrip_ambiguities": len(ambiguity_rows),
        "new_surface_forms": 0,
        "new_card_values": 0,
        "manuscript_event_claim": False,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
