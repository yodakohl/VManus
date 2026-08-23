#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXCEPTIONS = ROOT / "experiments/yolo/sidequest_semantic_rare_card_prediction_hundred_seventy_sixth/HUNDRED_SEVENTY_SIXTH_19_EXCEPTION_DECK.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_381_PROSE_MASTER_EDITION.tsv"


ORDER = [
    (1, "N1_MATERIAL_AND_TOOL", "MC071", "Pflanzengrundteil", "auf den unteren Teil des Pflanzenbilds zeigen"),
    (2, "N1_MATERIAL_AND_TOOL", "MC086", "abgeteilter Anteil", "eine Handvoll sichtbar in zwei Teile teilen"),
    (3, "N1_MATERIAL_AND_TOOL", "MC012", "kleiner Zusatz", "eine Prise in das aktive Gefaess geben"),
    (4, "N1_MATERIAL_AND_TOOL", "MC059", "Einlage oder Filterpolster", "ein gefaltetes Tuch in die Oeffnung legen"),
    (5, "N2_CONTAINER_AND_PLACE", "MC159", "Aufnahmegefaess", "auf das leere Empfaengergefaess zeigen"),
    (6, "N2_CONTAINER_AND_PLACE", "MC160", "Verwahrort", "das Gefaess an seinen Regal- oder Lagerplatz stellen"),
    (7, "N3_SEPARATE_AND_CLARIFY", "MC129", "Auswringen", "ein nasses Tuch mit beiden Haenden drehen"),
    (8, "N3_SEPARATE_AND_CLARIFY", "MC156", "Nachseihen", "die Fluessigkeit ein zweites Mal durch Tuch geben"),
    (9, "N3_SEPARATE_AND_CLARIFY", "MC141", "Klarlauf", "auf den klaren ausfliessenden Strom zeigen"),
    (10, "N3_SEPARATE_AND_CLARIFY", "MC066", "Klarabzug", "nur die klare obere Fluessigkeit abziehen"),
    (11, "N3_SEPARATE_AND_CLARIFY", "MC100", "Abkuehlen", "Hand vom warmen Gefaess wegnehmen und warten"),
    (12, "N3_SEPARATE_AND_CLARIFY", "MC152", "Teilen", "einen Posten auf zwei Gefaesse verteilen"),
    (13, "N4_WASH_AND_CLOSE", "MC130", "Waschgang", "Stelle oder Gefaess einmal waschen"),
    (14, "N4_WASH_AND_CLOSE", "MC038", "Waschgang abschliessen", "waschen und die Zelle sichtbar schliessen"),
    (15, "N4_WASH_AND_CLOSE", "MC084", "Waschfolge abschliessen", "letzte Waschung ausfuehren und absetzen"),
    (16, "N5_LINK_AND_ADMINISTER", "MC142", "vom vorigen Posten", "mit dem Griffel auf den vorherigen Ansatz zurueckzeigen"),
    (17, "N5_LINK_AND_ADMINISTER", "MC089", "aus der Quelle zugiessen", "vom Quellgefaess in die Zielstation giessen"),
    (18, "N5_LINK_AND_ADMINISTER", "MC068", "Folgeanwendung", "vom ersten zum naechsten Ziel weiterzeigen"),
    (19, "N5_LINK_AND_ADMINISTER", "MC164", "Einlage oder Arbeitsstelle festsetzen", "Einlage anlegen festbinden und die Zelle schliessen"),
]


DRAWERS = [
    ("N1_MATERIAL_AND_TOOL", 4, "Bildstoff teilen Zusatz und Einlage bereitstellen", "vor dem ersten Prozessschritt"),
    ("N2_CONTAINER_AND_PLACE", 2, "Empfaenger und Verwahrort unterscheiden", "beim Ueberfuehren oder Lagern"),
    ("N3_SEPARATE_AND_CLARIFY", 6, "auswringen nachseihen klar abziehen kuehlen und teilen", "bei der Produktklaerung"),
    ("N4_WASH_AND_CLOSE", 3, "Waschgang und dessen Abschluss markieren", "an Wasch- und Spuelstationen"),
    ("N5_LINK_AND_ADMINISTER", 4, "Vorbezug Quellzuguss Folgeanwendung und Festsetzen", "bei Recordfortsetzung oder Zielgebrauch"),
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
    source = {row["master_card_id"]: row for row in read(EXCEPTIONS)}
    rows = []
    for lesson_order, drawer, card_id, concise, gesture in ORDER:
        row = source[card_id]
        rows.append(
            {
                "lesson_order": lesson_order,
                "drawer": drawer,
                "master_card_id": card_id,
                "master_form": row["master_form"],
                "registered_surfaces": row["registered_surfaces"],
                "event_count": row["event_count"],
                "records": row["records"],
                "current_value_de": row["current_value_de"],
                "concise_nomenclator_value_de": concise,
                "productive_frame": row["literal_atoms"],
                "memorized_body": row["memorized_body"],
                "master_gesture_de": gesture,
                "reading_rule_de": row["teaching_rule_de"],
            }
        )
    write(OUT / "HUNDRED_SEVENTY_SEVENTH_19_CARD_NOMENCLATOR.tsv", rows)

    drawer_rows = [
        {
            "drawer": drawer,
            "card_count": count,
            "lesson_de": lesson,
            "use_point_de": use,
        }
        for drawer, count, lesson, use in DRAWERS
    ]
    write(OUT / "HUNDRED_SEVENTY_SEVENTH_5_NOMENCLATOR_DRAWERS.tsv", drawer_rows)

    event_source = read(EVENTS)
    ids = set(source)
    event_rows = []
    nomenclator = {row["master_card_id"]: row for row in rows}
    for row in event_source:
        if row["master_card_id"] not in ids:
            continue
        card = nomenclator[row["master_card_id"]]
        event_rows.append(
            {
                "event_serial": row["event_serial"],
                "record_unit_id": row["record_unit_id"],
                "statement_id": row["statement_id"],
                "page": row["page"],
                "visible_surface": row["visible_surface"],
                "master_card_id": row["master_card_id"],
                "drawer": card["drawer"],
                "nomenclator_value_de": card["concise_nomenclator_value_de"],
                "local_clause_de": row["complete_workshop_expansion_de"],
            }
        )
    write(OUT / "HUNDRED_SEVENTY_SEVENTH_24_EXCEPTION_OCCURRENCES.tsv", event_rows)

    summary = {
        "source_exception_sha256": hashlib.sha256(EXCEPTIONS.read_bytes()).hexdigest(),
        "source_event_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "nomenclator_cards": len(rows),
        "drawers": len(drawer_rows),
        "occurrences": len(event_rows),
        "drawer_counts": dict(Counter(row["drawer"] for row in rows)),
        "pure_wholes": sum(row["prediction_status"] == "MEMORIZED_WHOLE_CARD" for row in source.values()),
        "frame_plus_body": sum(row["prediction_status"] == "COMPOSED_FRAME_PLUS_MEMORIZED_BODY" for row in source.values()),
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
