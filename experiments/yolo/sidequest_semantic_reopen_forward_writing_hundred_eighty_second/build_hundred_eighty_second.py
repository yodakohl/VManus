#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"
GRAMMAR = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_REVISED_GRAMMAR_CARD.md"


TOKENS = [
    (1, 1, 1, "G1", "LOAD_PREVIOUS", "vorigen Ansatz aufnehmen", "MC142", "dchol", "NO"),
    (2, 1, 1, "G2", "SET_MEASURE", "Sollmass nehmen", "MC039", "aiin", "NO"),
    (3, 1, 1, "G3", "WARM", "kurz waermen", "MC147", "cheky", "NO"),
    (4, 1, 1, "G5", "SET_FIRST_TARGET", "am ersten Ziel einsetzen", "MC040", "okal", "NO"),
    (5, 1, 1, "G4", "SHORT_CONTACT", "kurz einwirken lassen", "MC007", "okey", "NO"),
    (6, 1, 2, "G2", "REOPEN_PORTION", "einen weiteren Anteil aufrufen", "MC105", "kain", "YES"),
    (7, 1, 2, "G4", "TRANSFER", "diesen Anteil ueberfuehren", "MC074", "chedy", "NO"),
    (8, 1, 2, "G5", "SET_THERE", "dorthin bringen", "MC154", "dal", "NO"),
    (9, 1, 3, "G2", "REOPEN_CLEAR_EXTRACT", "Klarauszug aufrufen", "MC119", "shey", "YES"),
    (10, 1, 3, "G2", "MEASURE_CLEAR_EXTRACT", "davon Sollmass nehmen", "MC039", "aiin", "NO"),
    (11, 1, 3, "G3", "SET_INSERT", "Einlage setzen", "MC059", "dain", "NO"),
    (12, 1, 3, "G4", "PASS_AND_CLOSE", "einmal durchlassen und Feld schliessen", "MC143", "shckhedy", "NO"),
    (13, 2, 1, "G5", "NEXT_ITEM", "zum Folgeposten wechseln", "MC107", "qotchy", "NO"),
    (14, 2, 1, "G5", "NEXT_TARGET", "danach zur naechsten Zielstelle", "MC093", "otal", "NO"),
    (15, 2, 1, "G5", "SET_NEXT_TARGET", "dort einsetzen", "MC026", "qoky", "NO"),
    (16, 2, 1, "G6", "WASH_CLOSE", "Waschgang schliessen", "MC038", "lshedy", "NO"),
    (17, 3, 1, "G2", "SELECT_REMAINDER", "Restanteil aufrufen", "MC105", "kain", "NO"),
    (18, 3, 1, "G3", "STORE", "am Verwahrort abstellen", "MC160", "talam", "NO"),
    (19, 3, 1, "G6", "READY_CLOSE", "fertig markieren", "MC019", "oldy", "NO"),
]


FIELDS = [
    (1, "dchol aiin cheky okal okey kain chedy dal shey aiin dain shckhedy", "Vorigen Ansatz messen, kurz waermen und am ersten Ziel kurz halten; weiteren Anteil dorthin ueberfuehren; Klarauszug messen, Einlage setzen und einmal durchlassen.", "CLOSED", 3),
    (2, "qotchy otal qoky lshedy", "Zum Folgeposten und naechsten Ziel wechseln, dort einsetzen und den Waschgang schliessen.", "CLOSED", 1),
    (3, "kain talam oldy", "Den Restanteil verwahren und fertig markieren.", "CLOSED", 1),
]


STATE_TRACE = [
    (1, 1, "PREVIOUS_BATCH", "MEASURED_WARM_PORTION_AT_TARGET_1", "TARGET_1", "CONTACT", "NO"),
    (1, 2, "PREVIOUS_BATCH", "SECOND_PORTION_TRANSFERRED", "TARGET_1", "TRANSFER", "YES"),
    (1, 3, "CLEAR_EXTRACT", "CLEAR_EXTRACT_PASSED_ONCE", "TARGET_1", "INSERT_PASS", "YES"),
    (2, 1, "CLEAR_EXTRACT", "TARGET_2_WASH_COMPLETE", "TARGET_2", "WASH", "NO"),
    (3, 1, "PREVIOUS_BATCH_REMAINDER", "REMAINDER_STORED_READY", "STORAGE", "STORAGE", "NO"),
]


AMBIGUITIES = [
    ("A1", "dchol", "welcher vorige Ansatz", "Beschriftung oder letzte aktive Charge des Werkstattzettels"),
    ("A2", "aiin", "Einheit des Sollmasses", "lokales Meistermass"),
    ("A3", "cheky", "genaue Temperatur", "gewohnte kurze Waermestufe"),
    ("A4", "okal okey", "Art der ersten Zielstelle und Kontaktdauer", "sichtbare Station plus kurze Werkstattstufe"),
    ("A5", "kain", "Groesse des weiteren Anteils und Restanteils", "Teilungsbrauch des aktiven Ansatzes"),
    ("A6", "dain shckhedy", "Material der Einlage und Art des Durchlasses", "lokales Werkzeug"),
    ("A7", "otal qoky lshedy", "Art des zweiten Ziels und Waschmedium", "sichtbarer Zielbesitzer und aktive Charge"),
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
    for order, field, packet, slot, step, reading, card_id, surface, reopen in TOKENS:
        card = dictionary[card_id]
        token_rows.append(
            {
                "token_order": order,
                "field": field,
                "micro_packet": packet,
                "grammar_slot": slot,
                "source_step": step,
                "source_instruction_de": reading,
                "master_card_id": card_id,
                "chosen_visible_surface": surface,
                "dictionary_value_de": card["portable_card_value_de"],
                "surface_is_registered": "YES" if surface in card["registered_surfaces"].split("|") else "NO",
                "reopen_before": reopen,
                "decoded_step_de": reading,
            }
        )
    write(OUT / "HUNDRED_EIGHTY_SECOND_19_TOKEN_REOPEN_ENCODING.tsv", token_rows)

    field_rows = [
        {
            "field": field,
            "visible_card_sequence": sequence,
            "fluent_reading_de": reading,
            "field_status": status,
            "micro_packets": packets,
            "sequence_source": "NEW_COMPOSITION",
        }
        for field, sequence, reading, status, packets in FIELDS
    ]
    write(OUT / "HUNDRED_EIGHTY_SECOND_3_FIELD_REOPEN_EXERCISE.tsv", field_rows)

    state_rows = [
        {
            "field": field,
            "micro_packet": packet,
            "batch_register": batch,
            "portion_register_after": portion,
            "target_register_after": target,
            "station_register_after": station,
            "explicit_reopen": reopen,
        }
        for field, packet, batch, portion, target, station, reopen in STATE_TRACE
    ]
    write(OUT / "HUNDRED_EIGHTY_SECOND_5_PACKET_STATE_TRACE.tsv", state_rows)

    ambiguity_rows = [
        {
            "ambiguity_id": aid,
            "surface_or_sequence": surface,
            "missing_information_de": missing,
            "workshop_resolution_de": resolution,
        }
        for aid, surface, missing, resolution in AMBIGUITIES
    ]
    write(OUT / "HUNDRED_EIGHTY_SECOND_7_LOCAL_AMBIGUITIES.tsv", ambiguity_rows)

    summary = {
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "grammar_sha256": hashlib.sha256(GRAMMAR.read_bytes()).hexdigest(),
        "tokens": len(token_rows),
        "distinct_cards": len({row["master_card_id"] for row in token_rows}),
        "fields": len(field_rows),
        "micro_packets": len(state_rows),
        "internal_reopens": sum(row["reopen_before"] == "YES" for row in token_rows),
        "all_fields_new": all(row["sequence_source"] == "NEW_COMPOSITION" for row in field_rows),
        "new_card_values": 0,
        "new_surface_forms": 0,
        "manuscript_event_claim": False,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
