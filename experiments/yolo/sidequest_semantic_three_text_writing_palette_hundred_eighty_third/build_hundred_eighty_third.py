#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
AB = ROOT / "experiments/yolo/sidequest_semantic_third_scribe_grammar_hundred_eightieth/HUNDRED_EIGHTIETH_29_TOKEN_SLOT_PARSE.tsv"
C = ROOT / "experiments/yolo/sidequest_semantic_reopen_forward_writing_hundred_eighty_second/HUNDRED_EIGHTY_SECOND_19_TOKEN_REOPEN_ENCODING.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"
RARE = ROOT / "experiments/yolo/sidequest_semantic_rare_card_prediction_hundred_seventy_sixth/HUNDRED_SEVENTY_SIXTH_143_RARE_CARD_PREDICTIONS.tsv"
NOMENCLATOR = ROOT / "experiments/yolo/sidequest_semantic_exception_nomenclator_hundred_seventy_seventh/HUNDRED_SEVENTY_SEVENTH_19_CARD_NOMENCLATOR.tsv"


SLOT_RULES = {
    "G1": ("QUELLE_KONTEXT", "Ansatz laden oder alten Vorrat wieder aufnehmen", "Ein fehlender Besitzer bleibt still; dchol und talam sind nicht synonym."),
    "G2": ("AUSWAHL_MASS_TEILUNG", "Produkt, Mass, Anteil oder Teilungszweig waehlen", "Mass und Portion duerfen nicht ohne Aenderung der Arbeitsanweisung vertauscht werden."),
    "G3": ("ZUSTAND_WERKZEUG_STATION", "Temperatur, Einlage, Verwahrort oder Prozesszustand setzen", "Gleiche Slotklasse bedeutet nicht gleichen Gegenstand."),
    "G4": ("VORGANG_KONTAKT", "ueberfuehren, kurz/lange halten oder durchlassen", "Auf eingebetteten Schluss achten; nach Schluss darf im Feld nichts folgen."),
    "G5": ("ZIEL_FOLGE", "gegenwaertiges oder folgendes Ziel adressieren und einsetzen", "Adresse, Zielaktion und Folgeschritt sind drei verschiedene Werte."),
    "G6": ("FREIGABE_SCHLUSS", "fertig, Waschschluss oder letzte Waschfolge markieren", "Die konkrete Abschlussart bleibt Teil der Kartenbedeutung."),
}


SUBSTITUTIONS = [
    ("P01", "aiin", "kain", "G2", "GRAMMATICAL_BUT_MEANING_CHANGES", "Sollmass wird zu Anteil"),
    ("P02", "kain", "ykain", "G2", "SAFE_BRANCH_SPECIALIZATION", "allgemeiner Anteil wird erster Anteil"),
    ("P03", "kain", "ykan", "G2", "SAFE_BRANCH_SPECIALIZATION", "allgemeiner Anteil wird zweiter Anteil"),
    ("P04", "aiin kain", "ykaiin", "G2", "SAFE_COMPRESSION_WITH_CONTEXT", "Mass plus Portion wird kompakte Sollportion"),
    ("P05", "cheky", "ody", "G3", "GRAMMATICAL_OPPOSITE_PROCESS", "kurzes Waermen wird Abkuehlen"),
    ("P06", "talam@G1", "talam@G3", "G1_G3", "SAME_CARD_CONTEXT_SHIFT", "Verwahrort lokalisiert erst Vorrat und spaeter Lagerhandlung"),
    ("P07", "okey", "qokedy", "G4", "SAFE_CLOSE_ADDITION", "kurzer Kontakt erhaelt einen Feldschluss"),
    ("P08", "qokedy", "qokeedy", "G4", "SAFE_GRADE_CHANGE", "kurzer geschlossener Kontakt wird langer geschlossener Kontakt"),
    ("P09", "dal", "okal", "G5", "GRAMMATICAL_ACTION_ADDITION", "blosse Zieladresse wird Ziel plus Einsetzen"),
    ("P10", "qoky", "otal", "G5", "UNSAFE_SEQUENCE_CHANGE", "Einsetzen am aktiven Ziel wird Wechsel zum naechsten Ziel"),
    ("P11", "lshedy", "rshedy", "G6", "LOCAL_WASH_VARIANT_ONLY", "Waschgangschluss wird Schluss der Waschfolge"),
    ("P12", "dchol", "talam", "G1", "NOT_SUBSTITUTABLE", "voriger Ansatz und Verwahrort setzen verschiedene Referenzen"),
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
    rare = {row["master_card_id"]: row for row in read(RARE)}
    nomenclator = {row["master_card_id"]: row for row in read(NOMENCLATOR)}
    usage = []
    for row in read(AB):
        usage.append(
            {
                "use_order": len(usage) + 1,
                "exercise": row["exercise"],
                "field": row["field"],
                "token_order": row["exercise_token_order"],
                "micro_packet": "NOT_EXPLICIT_IN_R180",
                "grammar_slot": row["grammar_slot"],
                "master_card_id": row["master_card_id"],
                "surface": row["surface"],
                "value_de": row["dictionary_value_de"],
            }
        )
    for row in read(C):
        usage.append(
            {
                "use_order": len(usage) + 1,
                "exercise": "C_REOPEN_THREE_PACKET",
                "field": row["field"],
                "token_order": row["token_order"],
                "micro_packet": row["micro_packet"],
                "grammar_slot": row["grammar_slot"],
                "master_card_id": row["master_card_id"],
                "surface": row["chosen_visible_surface"],
                "value_de": row["dictionary_value_de"],
            }
        )
    write(OUT / "HUNDRED_EIGHTY_THIRD_48_TOKEN_PALETTE_USAGE.tsv", usage)

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in usage:
        by_card[str(row["master_card_id"])].append(row)
    card_rows = []
    for card_id in sorted(by_card, key=lambda value: int(value[2:])):
        card = dictionary[card_id]
        rare_row = rare.get(card_id)
        if rare_row:
            teaching_class = rare_row["prediction_status"]
            literal_atoms = rare_row["literal_atoms"]
            memorized_body = rare_row["memorized_body"]
        else:
            teaching_class = "COMMON_WORKSHOP_CARD"
            literal_atoms = "COMMON_CARD_NOT_REPARSED_HERE"
            memorized_body = "NONE_OR_ALREADY_TAUGHT"
        if card_id in nomenclator:
            nomenclator_drawer = nomenclator[card_id]["drawer"]
            master_gesture = nomenclator[card_id]["master_gesture_de"]
        else:
            nomenclator_drawer = "NONE"
            master_gesture = "ordinary slot card; no separate exception gesture"
        uses = by_card[card_id]
        card_rows.append(
            {
                "master_card_id": card_id,
                "master_form": card["master_form"],
                "registered_surfaces": card["registered_surfaces"],
                "portable_value_de": card["portable_card_value_de"],
                "palette_slots": "|".join(sorted({str(row["grammar_slot"]) for row in uses})),
                "palette_use_count": len(uses),
                "exercises": "|".join(sorted({str(row["exercise"]) for row in uses})),
                "teaching_class": teaching_class,
                "literal_atoms": literal_atoms,
                "memorized_body": memorized_body,
                "nomenclator_drawer": nomenclator_drawer,
                "master_gesture_de": master_gesture,
            }
        )
    write(OUT / "HUNDRED_EIGHTY_THIRD_25_CARD_WRITING_PALETTE.tsv", card_rows)

    slot_rows = []
    for slot in [f"G{i}" for i in range(1, 7)]:
        cards = sorted({str(row["master_card_id"]) for row in usage if row["grammar_slot"] == slot}, key=lambda value: int(value[2:]))
        name, rule, warning = SLOT_RULES[slot]
        slot_rows.append(
            {
                "slot_id": slot,
                "slot_name": name,
                "distinct_cards_used": len(cards),
                "token_uses": sum(row["grammar_slot"] == slot for row in usage),
                "palette": " | ".join(f"{dictionary[card_id]['master_form']}={dictionary[card_id]['portable_card_value_de']}" for card_id in cards),
                "free_choice_rule_de": rule,
                "warning_de": warning,
            }
        )
    write(OUT / "HUNDRED_EIGHTY_THIRD_6_SLOT_WRITING_PALETTE.tsv", slot_rows)

    substitution_rows = [
        {
            "substitution_id": sid,
            "from_form": source,
            "to_form": target,
            "slot": slot,
            "status": status,
            "effect_de": effect,
        }
        for sid, source, target, slot, status, effect in SUBSTITUTIONS
    ]
    write(OUT / "HUNDRED_EIGHTY_THIRD_12_SUBSTITUTION_RULES.tsv", substitution_rows)

    class_counts = defaultdict(int)
    for row in card_rows:
        class_counts[str(row["teaching_class"])] += 1
    summary = {
        "ab_input_sha256": hashlib.sha256(AB.read_bytes()).hexdigest(),
        "c_input_sha256": hashlib.sha256(C.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "token_uses": len(usage),
        "distinct_cards": len(card_rows),
        "slot_memberships": sum(int(row["distinct_cards_used"]) for row in slot_rows),
        "slot_card_counts": {row["slot_id"]: int(row["distinct_cards_used"]) for row in slot_rows},
        "teaching_classes": dict(sorted(class_counts.items())),
        "substitution_rules": len(substitution_rows),
        "new_card_values": 0,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
