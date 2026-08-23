#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"
FIRST = ROOT / "experiments/yolo/sidequest_semantic_forward_writing_hundred_seventy_eighth/HUNDRED_SEVENTY_EIGHTH_13_TOKEN_FORWARD_ENCODING.tsv"


TOKENS = [
    (1, 1, "LOCATE_STOCK", "Verwahrort waehlen", "MC160", "talam"),
    (2, 1, "RESUME_STOCK", "vom vorigen Vorratsansatz nehmen", "MC142", "dchol"),
    (3, 1, "SELECT_MEASURED_PORTION", "Sollportion entnehmen", "MC170", "ykaiin"),
    (4, 1, "DIVIDE", "in zwei Teile teilen", "MC152", "ches"),
    (5, 2, "FIRST_PORTION", "erste Portion", "MC047", "ykain"),
    (6, 2, "COOL", "abkuehlen", "MC100", "ody"),
    (7, 2, "STORE", "am Verwahrort abstellen", "MC160", "talam"),
    (8, 2, "MARK_READY", "fertig markieren", "MC019", "oldy"),
    (9, 3, "SECOND_PORTION", "zweite Portion", "MC148", "ykan"),
    (10, 3, "WARM_BRIEFLY", "kurz waermen", "MC147", "cheky"),
    (11, 3, "SET_FIRST_TARGET", "an der ersten Zielstelle einsetzen", "MC040", "okal"),
    (12, 3, "SHORT_CONTACT_CLOSE", "kurz einwirken und schliessen", "MC083", "qokedy"),
    (13, 4, "NEXT_ITEM", "zum Folgeposten", "MC107", "qotchy"),
    (14, 4, "NEXT_TARGET", "danach zur naechsten Zielstelle", "MC093", "otal"),
    (15, 4, "SET_THERE", "dort einsetzen", "MC026", "qoky"),
    (16, 4, "WASH_CLOSE", "Waschfolge abschliessen", "MC084", "rshedy"),
]


FIELDS = [
    (1, "talam dchol ykaiin ches", "vom verwahrten vorigen Ansatz eine Sollportion nehmen und teilen", "OPEN"),
    (2, "ykain ody talam oldy", "erste Portion abkuehlen verwahren und fertig markieren", "CLOSED"),
    (3, "ykan cheky okal qokedy", "zweite Portion kurz waermen am ersten Ziel einsetzen und kurz einwirken", "CLOSED"),
    (4, "qotchy otal qoky rshedy", "zum naechsten Ziel wechseln dort einsetzen und die Waschfolge schliessen", "CLOSED"),
]


AMBIGUITIES = [
    ("B1", "talam dchol", "welcher Vorrat gemeint ist", "aktiver Herbalartikel oder beschriftetes Gefaess"),
    ("B2", "ykaiin", "Einheit der Sollportion", "Meistermass fuer diesen Vorrat"),
    ("B3", "ykain ykan", "physische Groesse der ersten und zweiten Portion", "Teilungsregel des Artikels"),
    ("B4", "cheky", "genaue Temperatur", "lokale milde Waermegewohnheit"),
    ("B5", "okal otal", "erste und naechste Zielstelle", "sichtbare Stationen oder gezeigte Koerperorte"),
    ("B6", "rshedy", "Waschmedium und Zahl der Bewegungen", "aktive Charge und lokaler Waschbrauch"),
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
    first_cards = {row["master_card_id"] for row in read(FIRST)}
    tokens = []
    for order, field, step, instruction, card_id, surface in TOKENS:
        card = dictionary[card_id]
        tokens.append(
            {
                "token_order": order,
                "field": field,
                "source_step": step,
                "source_instruction_de": instruction,
                "master_card_id": card_id,
                "chosen_visible_surface": surface,
                "dictionary_value_de": card["portable_card_value_de"],
                "surface_is_registered": "YES" if surface in card["registered_surfaces"].split("|") else "NO",
                "also_used_in_first_exercise": "YES" if card_id in first_cards else "NO",
                "decoded_step_de": instruction,
            }
        )
    write(OUT / "HUNDRED_SEVENTY_NINTH_16_TOKEN_STOCK_ENCODING.tsv", tokens)

    fields = [
        {
            "field": field,
            "visible_card_sequence": visible,
            "strict_atomic_reading_de": reading,
            "field_status": status,
            "sequence_source": "NEW_COMPOSITION",
        }
        for field, visible, reading, status in FIELDS
    ]
    write(OUT / "HUNDRED_SEVENTY_NINTH_4_FIELD_STOCK_EXERCISE.tsv", fields)

    ambiguities = [
        {
            "ambiguity_id": aid,
            "surface_or_sequence": surface,
            "missing_information_de": missing,
            "workshop_resolution_de": resolution,
        }
        for aid, surface, missing, resolution in AMBIGUITIES
    ]
    write(OUT / "HUNDRED_SEVENTY_NINTH_6_STOCK_AMBIGUITIES.tsv", ambiguities)

    summary = {
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "first_exercise_sha256": hashlib.sha256(FIRST.read_bytes()).hexdigest(),
        "tokens": len(tokens),
        "distinct_cards": len({row["master_card_id"] for row in tokens}),
        "fields": len(fields),
        "new_fields": len(fields),
        "cards_shared_with_first_exercise": len({row["master_card_id"] for row in tokens} & first_cards),
        "ambiguities": len(ambiguities),
        "new_surface_forms": 0,
        "new_card_values": 0,
        "manuscript_event_claim": False,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
