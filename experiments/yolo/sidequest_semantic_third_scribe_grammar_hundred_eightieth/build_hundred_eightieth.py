#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIRST = ROOT / "experiments/yolo/sidequest_semantic_forward_writing_hundred_seventy_eighth/HUNDRED_SEVENTY_EIGHTH_13_TOKEN_FORWARD_ENCODING.tsv"
SECOND = ROOT / "experiments/yolo/sidequest_semantic_second_forward_writing_hundred_seventy_ninth/HUNDRED_SEVENTY_NINTH_16_TOKEN_STOCK_ENCODING.tsv"


SLOTS = [
    {
        "slot_id": "G1",
        "slot_name_de": "QUELLE_UND_KONTEXT",
        "workshop_question_de": "Welcher Ansatz oder Vorrat ist aktiv?",
        "minimal_rule_de": "Besitzer, Verwahrort oder vorigen Ansatz aufnehmen.",
        "may_repeat": "YES",
        "may_be_omitted": "YES_IF_INHERITED",
    },
    {
        "slot_id": "G2",
        "slot_name_de": "AUSWAHL_MASS_UND_TEILUNG",
        "workshop_question_de": "Welche Menge oder Teilcharge wird bearbeitet?",
        "minimal_rule_de": "Posten waehlen, messen, teilen oder den ersten/zweiten Anteil binden.",
        "may_repeat": "YES",
        "may_be_omitted": "YES_IF_WHOLE_BATCH",
    },
    {
        "slot_id": "G3",
        "slot_name_de": "ZUSTAND_WERKZEUG_UND_STATION",
        "workshop_question_de": "Wie oder worin wird der Posten vorbereitet?",
        "minimal_rule_de": "Temperatur, Einlage, Gefaess oder Verwahrstation setzen.",
        "may_repeat": "YES",
        "may_be_omitted": "YES",
    },
    {
        "slot_id": "G4",
        "slot_name_de": "VORGANG_UND_KONTAKT",
        "workshop_question_de": "Was geschieht mit dem aktiven Posten?",
        "minimal_rule_de": "Ueberfuehren, halten, durchlassen oder einwirken lassen.",
        "may_repeat": "YES_AS_PASS_LOOP",
        "may_be_omitted": "NO_FOR_EXECUTION_FIELD",
    },
    {
        "slot_id": "G5",
        "slot_name_de": "ZIEL_UND_REIHENFOLGE",
        "workshop_question_de": "Wohin oder zu welchem Folgeposten geht der Vorgang?",
        "minimal_rule_de": "Zielstelle setzen oder zum naechsten Posten/Ziel wechseln.",
        "may_repeat": "YES",
        "may_be_omitted": "YES_IF_TARGET_INHERITED",
    },
    {
        "slot_id": "G6",
        "slot_name_de": "FREIGABE_WASCHUNG_UND_ABSCHLUSS",
        "workshop_question_de": "Ist der Teilschritt fertig und wie wird er beendet?",
        "minimal_rule_de": "Bereitschaft, Waschschluss oder sonstigen Feldabschluss setzen.",
        "may_repeat": "NO_WITHIN_FIELD",
        "may_be_omitted": "YES_IF_CLOSE_EMBEDDED_IN_G4",
    },
]


STEP_TO_SLOT = {
    "RESUME_PREVIOUS": "G1",
    "SELECT_CLEAR_EXTRACT": "G2",
    "SET_MEASURE": "G2",
    "WARM_BRIEFLY": "G3",
    "PLACE_INSERT": "G3",
    "TRANSFER_CHARGE": "G4",
    "HOLD_LONG_CLOSE": "G4",
    "FIRST_PASS_CLOSE": "G4",
    "SECOND_PASS_CLOSE": "G4",
    "SELECT_PORTION": "G2",
    "MOVE_TO_TARGET": "G5",
    "SET_AT_TARGET": "G5",
    "WASH_CLOSE": "G6",
    "LOCATE_STOCK": "G1",
    "RESUME_STOCK": "G1",
    "SELECT_MEASURED_PORTION": "G2",
    "DIVIDE": "G2",
    "FIRST_PORTION": "G2",
    "COOL": "G3",
    "STORE": "G3",
    "MARK_READY": "G6",
    "SECOND_PORTION": "G2",
    "SET_FIRST_TARGET": "G5",
    "SHORT_CONTACT_CLOSE": "G4",
    "NEXT_ITEM": "G5",
    "NEXT_TARGET": "G5",
    "SET_THERE": "G5",
}


REGISTERS = [
    {
        "register_id": "R_BATCH",
        "register_name_de": "AKTIVER_ANSATZ",
        "stores_de": "aktueller oder vom vorigen Feld fortgefuehrter Vorrat/Ansatz",
        "set_by_examples": "dchol|talam",
        "read_by_examples": "cheky|chedy|qokedy",
        "why_needed_de": "Ohne ihn ist 'vom vorigen' in beiden Anweisungen nicht ruecklesbar.",
    },
    {
        "register_id": "R_PORTION",
        "register_name_de": "AKTIVE_TEILCHARGE",
        "stores_de": "Sollmass, Anteil oder erster/zweiter Teil des aktiven Ansatzes",
        "set_by_examples": "aiin|kain|ykaiin|ykain|ykan",
        "read_by_examples": "qokeedy|okal|qokedy",
        "why_needed_de": "Die zweite Anweisung verzweigt einen Ansatz in zwei verschieden behandelte Teile.",
    },
    {
        "register_id": "R_TARGET",
        "register_name_de": "AKTIVE_ZIELSTELLE",
        "stores_de": "erste, gegenwaertige oder naechste Zielstelle",
        "set_by_examples": "dal|okal|otal|qoky",
        "read_by_examples": "lshedy|rshedy",
        "why_needed_de": "Waschung und Kontakt nennen ihr sichtbares Ziel nicht jedes Mal neu.",
    },
    {
        "register_id": "R_STATION",
        "register_name_de": "AKTIVES_WERKZEUG_ODER_GEFAESS",
        "stores_de": "Einlage, Verwahrort oder gegenwaertige Prozessstation",
        "set_by_examples": "dain|talam",
        "read_by_examples": "chedy|oldy|shckhedy",
        "why_needed_de": "Einlage und Verwahrort bleiben ueber die folgenden Handlungen still aktiv.",
    },
]


STATE_TRACE = [
    ("A_CLEAR_EXTRACT_DOUBLE_PASS", 1, "NONE", "PREVIOUS_CLEAR_EXTRACT", "PRESCRIBED_MEASURE", "UNSET", "UNSET", "Quelle und Sollmass binden"),
    ("A_CLEAR_EXTRACT_DOUBLE_PASS", 2, "PREVIOUS_CLEAR_EXTRACT", "WARM_TRANSFERRED_EXTRACT", "PRESCRIBED_MEASURE", "INHERITED", "INSERT", "waermen, Einlage setzen, ueberfuehren, lange halten"),
    ("A_CLEAR_EXTRACT_DOUBLE_PASS", 3, "WARM_TRANSFERRED_EXTRACT", "AFTER_PASS_1", "INHERITED", "INHERITED", "PASS_STATION", "erster Durchgang"),
    ("A_CLEAR_EXTRACT_DOUBLE_PASS", 4, "AFTER_PASS_1", "AFTER_PASS_2", "INHERITED", "INHERITED", "PASS_STATION", "zweiter Durchgang"),
    ("A_CLEAR_EXTRACT_DOUBLE_PASS", 5, "AFTER_PASS_2", "READY_FOR_TARGET_WASH", "SELECTED_PORTION", "TARGET_1", "WASH_STATION", "Anteil zum Ziel bringen, einsetzen, waschen"),
    ("B_STOCK_TWO_TARGET", 1, "NONE", "PREVIOUS_STOCK", "DIVIDED_INTO_1_AND_2", "UNSET", "STORAGE", "Vorrat aufnehmen, Sollportion teilen"),
    ("B_STOCK_TWO_TARGET", 2, "PREVIOUS_STOCK", "PREVIOUS_STOCK", "PORTION_1_STORED_READY", "STORAGE", "STORAGE", "ersten Teil kuehlen und verwahren"),
    ("B_STOCK_TWO_TARGET", 3, "PREVIOUS_STOCK", "PREVIOUS_STOCK", "PORTION_2_IN_CONTACT", "TARGET_1", "CONTACT_STATION", "zweiten Teil waermen, einsetzen, kurz halten"),
    ("B_STOCK_TWO_TARGET", 4, "PREVIOUS_STOCK", "WORKFLOW_COMPLETE", "PORTION_2", "TARGET_2", "WASH_STATION", "zum naechsten Ziel wechseln und waschen"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def compact_path(values: list[str]) -> str:
    result = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return ">".join(result)


def main() -> None:
    first = read(FIRST)
    second = read(SECOND)
    combined = []
    for exercise, rows in [("A_CLEAR_EXTRACT_DOUBLE_PASS", first), ("B_STOCK_TWO_TARGET", second)]:
        for row in rows:
            slot = STEP_TO_SLOT[row["source_step"]]
            combined.append(
                {
                    "global_token_order": len(combined) + 1,
                    "exercise": exercise,
                    "exercise_token_order": row["token_order"],
                    "field": row["field"],
                    "master_card_id": row["master_card_id"],
                    "surface": row["chosen_visible_surface"],
                    "source_step": row["source_step"],
                    "dictionary_value_de": row["dictionary_value_de"],
                    "grammar_slot": slot,
                    "slot_reading_de": next(item["slot_name_de"] for item in SLOTS if item["slot_id"] == slot),
                    "embedded_close": "YES" if "CLOSE" in row["source_step"] else "NO",
                }
            )
    write(OUT / "HUNDRED_EIGHTIETH_29_TOKEN_SLOT_PARSE.tsv", combined)
    write(OUT / "HUNDRED_EIGHTIETH_6_SHARED_SLOTS.tsv", SLOTS)
    write(OUT / "HUNDRED_EIGHTIETH_4_STATE_REGISTERS.tsv", REGISTERS)

    field_rows = []
    for exercise in ["A_CLEAR_EXTRACT_DOUBLE_PASS", "B_STOCK_TWO_TARGET"]:
        exercise_rows = [row for row in combined if row["exercise"] == exercise]
        for field in sorted({int(row["field"]) for row in exercise_rows}):
            rows = [row for row in exercise_rows if int(row["field"]) == field]
            field_rows.append(
                {
                    "exercise": exercise,
                    "field": field,
                    "visible_sequence": " ".join(row["surface"] for row in rows),
                    "slot_sequence": ">".join(row["grammar_slot"] for row in rows),
                    "compacted_slot_path": compact_path([row["grammar_slot"] for row in rows]),
                    "contains_embedded_close": "YES" if any(row["embedded_close"] == "YES" for row in rows) else "NO",
                    "field_lesson_de": next(item[-1] for item in STATE_TRACE if item[0] == exercise and item[1] == field),
                }
            )
    write(OUT / "HUNDRED_EIGHTIETH_9_FIELD_GRAMMAR_TRACES.tsv", field_rows)

    state_rows = [
        {
            "exercise": exercise,
            "field": field,
            "batch_before": batch_before,
            "batch_after": batch_after,
            "portion_after": portion,
            "target_after": target,
            "station_after": station,
            "plain_transition_de": lesson,
        }
        for exercise, field, batch_before, batch_after, portion, target, station, lesson in STATE_TRACE
    ]
    write(OUT / "HUNDRED_EIGHTIETH_9_FIELD_STATE_TRACES.tsv", state_rows)

    first_ids = {row["master_card_id"] for row in first}
    second_ids = {row["master_card_id"] for row in second}
    summary = {
        "first_input_sha256": hashlib.sha256(FIRST.read_bytes()).hexdigest(),
        "second_input_sha256": hashlib.sha256(SECOND.read_bytes()).hexdigest(),
        "tokens": len(combined),
        "fields": len(field_rows),
        "shared_slots": len(SLOTS),
        "state_registers": len(REGISTERS),
        "distinct_card_union": len(first_ids | second_ids),
        "shared_cards": sorted(first_ids & second_ids),
        "exercise_a_uses_all_slots": sorted({row["grammar_slot"] for row in combined if row["exercise"].startswith("A_")}),
        "exercise_b_uses_all_slots": sorted({row["grammar_slot"] for row in combined if row["exercise"].startswith("B_")}),
        "new_card_values": 0,
        "new_surface_forms": 0,
        "manuscript_event_claim": False,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
