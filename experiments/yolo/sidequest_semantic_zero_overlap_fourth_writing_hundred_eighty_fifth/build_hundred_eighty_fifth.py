#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"
SHORTLIST = ROOT / "experiments/yolo/sidequest_semantic_full_slot_lexicon_hundred_eighty_fourth/HUNDRED_EIGHTY_FOURTH_24_LOW_OVERLAP_SHORTLIST.tsv"
OLD_PALETTE = ROOT / "experiments/yolo/sidequest_semantic_three_text_writing_palette_hundred_eighty_third/HUNDRED_EIGHTY_THIRD_25_CARD_WRITING_PALETTE.tsv"


TOKENS = [
    (1, 1, "G1", "LOAD_BATCH", "Ansatz aufnehmen", "MC080", "chor"),
    (2, 1, "G1", "TAKE_FROM_IT", "davon nehmen", "MC055", "char"),
    (3, 1, "G2", "MEASURE", "bemessen", "MC120", "okaiin"),
    (4, 1, "G1", "ADD_SUPPLEMENT", "Zusatz bereitstellen", "MC012", "dl"),
    (5, 1, "G2", "ADD_OTHER_INGREDIENT", "weitere Zutat zugeben", "MC034", "cho"),
    (6, 1, "G3", "PREPARE_SHORT", "kurz vorbereiten", "MC073", "qcthey"),
    (7, 1, "G4", "CONTINUE", "weiterarbeiten", "MC153", "cheol"),
    (8, 2, "G2", "SELECT_THIS", "diesen Posten aufnehmen", "MC123", "chey"),
    (9, 2, "G3", "WORK_LONGER", "laenger bearbeiten", "MC032", "cheeky"),
    (10, 2, "G5", "SETTLE_AT_TARGET", "am Ziel absetzen", "MC113", "shedal"),
    (11, 2, "G6", "SETTLE_CLOSE", "kurz absetzen und schliessen", "MC128", "cheedy"),
    (12, 3, "G1", "LOAD_FOLLOW_BATCH", "Folgeansatz aufnehmen", "MC013", "otchor"),
    (13, 3, "G2", "ADD_PORTION", "einen Anteil zugeben", "MC017", "okain"),
    (14, 3, "G3", "SET_WORK_STAGE", "Arbeitsstufe setzen", "MC033", "oiiin"),
    (15, 3, "G5", "TARGET_TRANSFER", "zum Ziel ueberfuehren", "MC001", "chdal"),
    (16, 3, "G4", "TRANSFER_CLOSE", "ueberfuehren und schliessen", "MC025", "dchedy"),
    (17, 4, "G2", "SELECT_THIS_AGAIN", "diesen Posten aufnehmen", "MC123", "chey"),
    (18, 4, "G4", "LONG_CONTACT", "lange einwirken lassen", "MC002", "okeey"),
    (19, 4, "G5", "TARGET_TRANSFER_AGAIN", "zum Ziel ueberfuehren", "MC001", "chdal"),
    (20, 4, "G4", "DRAIN_CLOSE", "abfuehren und schliessen", "MC155", "lchedy"),
    (21, 5, "G1", "LOAD_NEXT_BATCH", "Folgeansatz aufnehmen", "MC013", "otchor"),
    (22, 5, "G2", "ADD_OTHER_INGREDIENT_AGAIN", "weitere Zutat zugeben", "MC034", "cho"),
    (23, 5, "G3", "PREPARE_SHORT_AGAIN", "kurz vorbereiten", "MC073", "qcthey"),
    (24, 5, "G5", "COLLECT_LONG", "lange sammeln", "MC020", "solkeey"),
    (25, 5, "G6", "DRAW_OFF_CLOSE", "abziehen und schliessen", "MC004", "ldy"),
]


FIELDS = [
    (1, "chor char okaiin dl cho qcthey cheol", "Ansatz aufnehmen, davon bemessen, Zusatz und weitere Zutat zugeben, kurz vorbereiten und weiterarbeiten.", "OPEN"),
    (2, "chey cheeky shedal cheedy", "Diesen Posten laenger bearbeiten, am Ziel absetzen und den kurzen Absetzschritt schliessen.", "CLOSED"),
    (3, "otchor okain oiiin chdal dchedy", "Folgeansatz mit einer Portion auf die Arbeitsstufe setzen, zum Ziel ueberfuehren und schliessen.", "CLOSED"),
    (4, "chey okeey chdal lchedy", "Diesen Posten lange einwirken lassen, zum Ziel ueberfuehren und abfuehren.", "CLOSED"),
    (5, "otchor cho qcthey solkeey ldy", "Folgeansatz mit weiterer Zutat kurz vorbereiten, lange sammeln, abziehen und schliessen.", "CLOSED"),
]


AMBIGUITIES = [
    ("A1", "chor char", "welcher Ansatz und welcher Teil davon", "aktiver Bild- oder Gefaessbesitzer"),
    ("A2", "okaiin", "Einheit des Masses", "Meistermass des jeweiligen Ansatzes"),
    ("A3", "dl cho", "konkreter Zusatz und weitere Zutat", "lokale Beschriftung oder Bildargument"),
    ("A4", "cheeky", "Dauer der laengeren Bearbeitung", "Werkstattgrad EE"),
    ("A5", "shedal chdal", "physische Zielstelle", "sichtbare Station"),
    ("A6", "solkeey", "Sammelgefaess und Dauer", "lokale Sammelstation plus Langgrad"),
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
    shortlist = {row["master_card_id"]: row for row in read(SHORTLIST)}
    old_palette = {row["master_card_id"] for row in read(OLD_PALETTE)}
    token_rows = []
    for order, field, slot, step, reading, card_id, surface in TOKENS:
        card = dictionary[card_id]
        finality = shortlist[card_id]["finality_rule"]
        field_last = order in {7, 11, 16, 20, 25}
        token_rows.append(
            {
                "token_order": order,
                "field": field,
                "grammar_slot": slot,
                "source_step": step,
                "source_instruction_de": reading,
                "master_card_id": card_id,
                "surface": surface,
                "dictionary_value_de": card["portable_card_value_de"],
                "on_24_card_shortlist": "YES" if card_id in shortlist else "NO",
                "in_previous_25_card_palette": "YES" if card_id in old_palette else "NO",
                "surface_is_registered": "YES" if surface in card["registered_surfaces"].split("|") else "NO",
                "observed_finality_rule": finality,
                "field_final": "YES" if field_last else "NO",
                "decoded_step_de": reading,
            }
        )
    write(OUT / "HUNDRED_EIGHTY_FIFTH_25_TOKEN_ZERO_OVERLAP_ENCODING.tsv", token_rows)

    field_rows = [
        {
            "field": field,
            "visible_sequence": sequence,
            "fluent_reading_de": reading,
            "field_status": status,
            "sequence_source": "NEW_COMPOSITION_FROM_UNUSED_SHORTLIST",
        }
        for field, sequence, reading, status in FIELDS
    ]
    write(OUT / "HUNDRED_EIGHTY_FIFTH_5_FIELD_FOURTH_EXERCISE.tsv", field_rows)

    ambiguity_rows = [
        {
            "ambiguity_id": aid,
            "surface_or_sequence": surface,
            "missing_information_de": missing,
            "workshop_resolution_de": resolution,
        }
        for aid, surface, missing, resolution in AMBIGUITIES
    ]
    write(OUT / "HUNDRED_EIGHTY_FIFTH_6_LOCAL_AMBIGUITIES.tsv", ambiguity_rows)

    card_rows = []
    for card_id in sorted({row[5] for row in TOKENS}, key=lambda value: int(value[2:])):
        card = dictionary[card_id]
        uses = [row for row in token_rows if row["master_card_id"] == card_id]
        card_rows.append(
            {
                "master_card_id": card_id,
                "master_form": card["master_form"],
                "value_de": card["portable_card_value_de"],
                "slot": shortlist[card_id]["slot"],
                "use_count": len(uses),
                "previous_palette_overlap": "YES" if card_id in old_palette else "NO",
                "finality_rule": shortlist[card_id]["finality_rule"],
            }
        )
    write(OUT / "HUNDRED_EIGHTY_FIFTH_20_CARD_LOW_OVERLAP_INVENTORY.tsv", card_rows)

    summary = {
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "shortlist_sha256": hashlib.sha256(SHORTLIST.read_bytes()).hexdigest(),
        "old_palette_sha256": hashlib.sha256(OLD_PALETTE.read_bytes()).hexdigest(),
        "tokens": len(token_rows),
        "distinct_cards": len(card_rows),
        "fields": len(field_rows),
        "shortlist_cards_used": len({row["master_card_id"] for row in token_rows if row["on_24_card_shortlist"] == "YES"}),
        "previous_palette_card_overlap": len({row["master_card_id"] for row in token_rows if row["in_previous_25_card_palette"] == "YES"}),
        "new_card_values": 0,
        "new_surface_forms": 0,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
